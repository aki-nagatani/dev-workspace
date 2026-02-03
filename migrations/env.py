from __future__ import annotations
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Alembic Config object
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add project src directories to sys.path
script_location = config.get_main_option("script_location")
if script_location:
    alembic_dir = Path(script_location).resolve().parent
    workspace_root = alembic_dir.parent
    
    # Add FishTrack, MyPokedex, and otayori-navi src directories to path
    fishtrack_src = workspace_root.parent / "FishTrack" / "src"
    mypokedex_src = workspace_root.parent / "MyPokedex" / "src"
    otayori_src = workspace_root.parent / "otayori-navi" / "src"
    
    for src_dir in [fishtrack_src, mypokedex_src, otayori_src]:
        if src_dir.exists() and str(src_dir) not in sys.path:
            sys.path.insert(0, str(src_dir))

# Import both FishTrack and MyPokedex models to build unified metadata
# FishTrackモジュールはオプショナル（MyPokedexのみのデプロイ時には利用できない可能性がある）
target_metadata = None
fishtrack_db = None
mypokedex_db = None
otayori_metadata = None

try:
    # Create Flask app contexts to ensure models are properly registered
    from flask import Flask
    from sqlalchemy import MetaData
    
    # Try to import FishTrack models (optional)
    fishtrack_db = None
    try:
        # FishTrack app context
        fishtrack_app = Flask(__name__)
        fishtrack_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        fishtrack_app.config['SQLALCHEMY_BINDS'] = {'fishtrack': 'sqlite:///:memory:'}
        from fishtrack.extensions import db as fishtrack_db
        fishtrack_db.init_app(fishtrack_app)
        
        with fishtrack_app.app_context():
            # Import all models to ensure they are registered
            from fishtrack.models import (  # noqa: F401
                Manufacturer,
                RodHolding,
                RodModel,
                RodSeries,
                ReelHolding,
                ReelModel,
                ReelSeries,
                FishTrackUser,
                TackleSpecImportLog,
                OpsMonitoring,
            )
            
            # Flask-SQLAlchemy with __bind_key__ may register tables in separate metadata
            # We need to ensure all tables are in fishtrack_db.metadata
            # Force registration by accessing __table__ attribute
            for model_class in [Manufacturer, RodHolding, RodModel, RodSeries,
                               ReelHolding, ReelModel, ReelSeries, FishTrackUser,
                               TackleSpecImportLog, OpsMonitoring]:
                if hasattr(model_class, '__table__') and model_class.__table__ is not None:
                    table = model_class.__table__
                    # If table is not in metadata, add it
                    if table.name not in fishtrack_db.metadata.tables:
                        # Copy table to fishtrack_db.metadata
                        table.to_metadata(fishtrack_db.metadata, schema=table.schema)
    except (ImportError, ModuleNotFoundError) as e:
        # FishTrackモジュールが利用できない場合（MyPokedexのみのデプロイ時など）
        print(f"Info: FishTrack module not available: {e}")
        print("   Continuing with MyPokedex models only...")
        fishtrack_db = None
    except Exception as e:
        print(f"Warning: Could not import FishTrack models: {e}")
        fishtrack_db = None
    
    # MyPokedex app context (required)
    mypokedex_app = Flask(__name__)
    mypokedex_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    from mypokedex.extensions import db as mypokedex_db
    mypokedex_db.init_app(mypokedex_app)
    
    with mypokedex_app.app_context():
        from mypokedex.models import (  # noqa: F401
            User,
            Pokemon,
            GameTitle,
            Regist,
            PartyMember,
            BoxMember,
            UserGameSetting,
            Evolution,
            Contact,
        )
        # DexEntry and Placement are not exported from mypokedex.models.__init__, import directly
        from mypokedex.models.dex_entry import DexEntry  # noqa: F401
        from mypokedex.models.placement import Placement  # noqa: F401
    
    # Import otayori-navi models (DeclarativeBase)
    try:
        from otayori_navi.models import Base as otayori_base  # noqa: F401

        otayori_metadata = otayori_base.metadata
    except (ImportError, ModuleNotFoundError) as e:
        print(f"Info: otayori-navi module not available: {e}")
        otayori_metadata = None
    except Exception as e:
        print(f"Warning: Could not import otayori-navi models: {e}")
        otayori_metadata = None

    # Combine metadata from projects
    # Since SQLAlchemy tables are bound to their metadata objects, we need to
    # create a unified metadata. The simplest approach is to use one metadata
    # as the base and add tables from the other, but tables can't be easily
    # moved between metadata objects.
    #
    # Instead, we'll create a new MetaData and use Table.tometadata() to copy
    # tables from both metadata objects to the new unified metadata.
    
    # Create a unified metadata object
    target_metadata = MetaData()
    
    # Copy all tables from FishTrack metadata to the unified metadata (if available)
    if fishtrack_db is not None:
        for table_name, table in fishtrack_db.metadata.tables.items():
            table.to_metadata(target_metadata, schema=table.schema)
    
    # Copy all tables from MyPokedex metadata to the unified metadata
    for table_name, table in mypokedex_db.metadata.tables.items():
        # Check for name conflicts
        if table_name not in target_metadata.tables:
            table.to_metadata(target_metadata, schema=table.schema)
        else:
            # If there's a conflict, log a warning
            print(f"Warning: Table {table_name} exists in both projects. Using first definition.")

    # Copy all tables from otayori-navi metadata (if available)
    if otayori_metadata is not None:
        for table_name, table in otayori_metadata.tables.items():
            if table_name not in target_metadata.tables:
                table.to_metadata(target_metadata, schema=table.schema)
            else:
                print(
                    f"Warning: Table {table_name} exists in multiple projects. Using first definition."
                )
    
except Exception as e:
    print(f"Warning: Could not import models: {e}")
    import traceback
    traceback.print_exc()
    target_metadata = None


def get_database_url() -> str:
    """Get database URL from environment variables.
    
    Priority:
    1. SHARED_DATABASE_URL
    2. SHARED_DB_URL
    3. FISHTRACK_DATABASE_URL (for backward compatibility)
    4. MYPDEX_DATABASE_URL (for backward compatibility)
    5. DB_URL (generic fallback)
    """
    url = (
        os.getenv("SHARED_DATABASE_URL")
        or os.getenv("SHARED_DB_URL")
        or os.getenv("FISHTRACK_DATABASE_URL")
        or os.getenv("MYPDEX_DATABASE_URL")
        or os.getenv("DB_URL")
        or config.get_main_option("sqlalchemy.url")
    )
    
    if not url:
        raise RuntimeError(
            "データベースURLが設定されていません。\n"
            "環境変数（SHARED_DATABASE_URL, SHARED_DB_URL, FISHTRACK_DATABASE_URL, "
            "MYPDEX_DATABASE_URL, DB_URL）のいずれかを設定してください。"
        )
    
    return url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    url = get_database_url()
    section = config.get_section(config.config_ini_section) or {}
    if url:
        section["sqlalchemy.url"] = url
    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

