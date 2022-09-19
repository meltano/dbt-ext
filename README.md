# dbt-ext

Meltano dbt utility extension

## Configuration

Note the new `DBT_EXT_TYPE` setting, used to indicate what dbt profile should be used, and new default executable of
`dbt_invoker` instead of `dbt`.

### dbt-postgres

```yaml
plugins:
  utilities:
    - name: dbt-postgres
      label: dbt PostgreSQL extension
      executable: dbt_invoker
      namespace: dbt_ext
      pip_url: dbt-core~=1.1.0 dbt-postgres~=1.1.0 git+https://github.com/meltano/dbt-ext.git@feat/working-dbt-ext
      settings:
      - name: ext_type
        env: DBT_EXT_TYPE
        value: postgres
      - name: project_dir
        label: Projects Directory
        value: $MELTANO_PROJECT_ROOT/transform
      - name: profiles_dir
        label: Profiles Directory
        value: $MELTANO_PROJECT_ROOT/transform/profiles/postgres
        env: DBT_PROFILES_DIR
        # Postgres connection settings are set via `config:` blocks and mapped to `profiles.yml`
      - name: host
        label: Host
        kind: string
        description: |
          The postgres host to connect to.
      - name: user
        label: User
        kind: string
        description: |
          The user to connect as.
      - name: password
        label: Password
        kind: password
        description: |
          The password to connect with.
      - name: port
        label: Port
        kind: integer
        description: |
          The port to connect to.
      - name: dbname
        label: Database
        aliases: ["database"]
        kind: string
        description: |
          The db to connect to.
      - name: schema
        label: Schema
        kind: string
        description: |
          The schema to use.
      - name: keepalives_idle
        label: Keep Alives Idle
        kind: integer
        description: |
          Seconds between TCP keepalive packets.
      - name: search_path
        label: Search Path
        kind: string
        description: |
          Overrides the default search path.
      - name: role
        label: Role
        kind: string
        description: |
          Role for dbt to assume when executing queries.
      - name: sslmode
        label: SSL Mode
        kind: array
        description: |
          SSL Mode used to connect to the database.
      commands:
        clean:
          args: clean
          description: Delete all folders in the clean-targets list (usually the dbt_modules and target directories.)
        compile:
          args: compile
          description: Generates executable SQL from source model, test, and analysis files. Compiled SQL files are written to the target/ directory.
        deps:
          args: deps
          description: Pull the most recent version of the dependencies listed in packages.yml
        run:
          args: run
          description: Compile SQL and execute against the current target database.
        seed:
          args: seed
          description: Load data from csv files into your data warehouse.
        snapshot:
          args: snapshot
          description: Execute snapshots defined in your project.
        test:
          args: test
          description: Runs tests on data in deployed models.
        freshness:
          args: source freshness
          description: Check the freshness of your source data.
        build:
          args: build
          description: Will run your models, tests, snapshots and seeds in DAG order.
        docs-generate:
          args: docs generate
          description: Generate documentation for your project.
        docs-serve:
          args: docs serve
          description: Serve documentation for your project. Make sure you ran `docs-generate` first.
        debug:
          args: debug
          description: Debug your DBT project and warehouse connection.
        describe:
          args: describe
          executable: dbt_extension
        initialize:
          args: initialize
          executable: dbt_extension
```

### dbt-snowflake

```yaml
  - name: dbt-snowflake
    label: dbt Snowflake
    executable: dbt_invoker
    namespace: dbt_ext
    settings:
    - name: project_dir
      label: Projects Directory
      value: $MELTANO_PROJECT_ROOT/transform
    - name: profiles_dir
      label: Profiles Directory
      env: DBT_PROFILES_DIR
      value: $MELTANO_PROJECT_ROOT/transform/profiles/snowflake
    - name: account
      label: Account
      kind: string
      description: The snowflake account to connect to.
    - name: user
      label: User
      kind: string
      description: The user to connect as.
    - name: password
      label: Password
      kind: password
      description: The user password to authenticate with.
    - name: role
      label: Role
      kind: string
      description: The user role to assume.
    - name: warehouse
      label: Warehouse
      kind: string
      description: The compute warehouse to use when building models.
    - name: database
      label: Database
      kind: string
      description: The database to create models in.
    - name: schema
      label: Schema
      kind: string
      description: The schema to build models into by default.
    commands:
      clean:
        args: clean
        description: Delete all folders in the clean-targets list (usually the dbt_modules
          and target directories.)
      compile:
        args: compile
        description: Generates executable SQL from source model, test, and analysis files.
          Compiled SQL files are written to the target/ directory.
      deps:
        args: deps
        description: Pull the most recent version of the dependencies listed in packages.yml
      run:
        args: run
        description: Compile SQL and execute against the current target database.
      seed:
        args: seed
        description: Load data from csv files into your data warehouse.
      snapshot:
        args: snapshot
        description: Execute snapshots defined in your project.
      test:
        args: test
        description: Runs tests on data in deployed models.
      freshness:
        args: source freshness
        description: Check the freshness of your source data.
      build:
        args: build
        description: Will run your models, tests, snapshots and seeds in DAG order.
      docs-generate:
        args: docs generate
        description: Generate documentation for your project.
      docs-serve:
        args: docs serve
        description: Serve documentation for your project. Make sure you ran `docs-generate` first.
      debug:
        args: debug
        description: Debug your DBT project and warehouse connection.
      describe:
        args: describe
        executable: dbt_extension
      initialize:
        args: initialize
        executable: dbt_extension
```


## Installation

```bash
meltano install utility dbt-postgres
meltano invoke dbt-postgres:initialize
meltano invoke dbt-postgres list
meltano invoke dbt-postgres test
```
