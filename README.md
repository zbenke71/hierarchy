# Hierarchy Package

## Overview

The `hierarchy` package provides tools to create, manage, and manipulate hierarchical data structures, under the `gyermelyi` namespace. It supports input from various sources such as lists, tuples, and pandas DataFrames. Additionally, it allows for reading from and writing to Oracle databases.

## Installation

To use the `hierarchy` package, ensure the directory structure matches the following:

```
hierarchy/
├── gyermelyi/
│   └── hierarchy/
│       ├── __init__.py
│       ├── hierarchy.py
│       └── hierarchydb.py
```

Then, you can import the package in your Python code.

## Usage

### Initialization

You can initialize a `Hierarchy` object with a source parameter or a configuration file.

```python
from gyermelyi.hierarchy import Hierarchy

# Initialize with a list of parent-child pairs
source = [['parent1', 'child1'], ['parent1', 'child2'], ['parent2', 'child3']]
hierarchy = Hierarchy(source=source)

# Initialize with a configuration file for database connection
config_file = 'path/to/config.ini'
hierarchy = Hierarchy(config_file=config_file)
```

### Creating Hierarchy

To create the hierarchical structure from the source data:

```python
hierarchy.create_hierarchy()
```

### Converting Hierarchy

The hierarchical data can be converted to different formats:

#### To Tuples

```python
tuples = hierarchy.to_tuples(flattened=True, empty_value=None, has_primkey=True)
```

#### To Lists

```python
lists = hierarchy.to_lists(flattened=True, empty_value=None, has_primkey=True)
```

#### To DataFrame

```python
df = hierarchy.to_dataframe(empty_value=None, level_label=None, has_primkey=True, primkey_label=None)
```

### Reading from Database

To read source data from a database:

```python
hierarchy.read_source_from_db()
```

### Writing to Database

To write the hierarchical data to a database:

```python
hierarchy.to_database(empty_value=None, level_label=None, has_primkey=True, primkey_label=None)
```

## Configuration

The configuration file should contain the necessary information for database connection and source/destination settings. Example:

```ini
[database]
user = your_username
password = your_password
dsn = your_dsn

[source]
schema = source_schema
table = source_table
parent = parent_column
child = child_column
where = optional_where_clause

[destination]
schema = destination_schema
table = destination_table
level = level_prefix
primkey = primary_key_column
```

## Classes

### Hierarchy

#### Methods

- `__init__(self, source=None, config_file=None)`: Initialize the Hierarchy object with source data or a configuration file.
- `_validate(self, source, config_file)`: Validate the source data and the config_file for the hierarchy.
- `create_hierarchy(self)`: Create the hierarchical structure from the source data.
- `delete_hierarchy(self)`: Delete the current hierarchy, setting it to None.
- `_flatten_hierarchy(self, *args)`: Flatten the hierarchical structure into a list of tuples.
- `to_tuples(self, *, flattened=True, empty_value=None, has_primkey=True)`: Get the hierarchical structure as a set of tuples.
- `to_lists(self, *, flattened=True, empty_value=None, has_primkey=True)`: Get the hierarchical structure as a list of lists.
- `to_dataframe(self, *, empty_value=None, level_label=None, has_primkey=True, primkey_label=None)`: Convert the hierarchical structure into a pandas DataFrame.
- `read_source_from_db(self)`: Read the source data from the database and update the source attribute.
- `to_database(self, *, empty_value=None, level_label=None, has_primkey=True, primkey_label=None, **kwargs)`: Write the hierarchy data to the database.

### HierarchyDB

An abstract base class for database operations.

#### Methods

- `read_data(self, *, schema=None, table=None, parent=None, child=None)`: Abstract method to read data from the database.
- `write_data(self, df, *, schema=None, table=None)`: Abstract method to write data to the database.

### HierarchyDBOracle

A class for interacting with an Oracle database to read and write hierarchy data.

#### Methods

- `__init__(self, *, user=None, password=None, dsn=None, **kwargs)`: Initialize the HierarchyDBOracle with database connection parameters.
- `_create_engine(self)`: Create a SQLAlchemy engine for connecting to the Oracle database.
- `read_data(self, *, schema=None, table=None, parent=None, child=None, where='', **kwargs)`: Read hierarchy data from the specified database table.
- `write_data(self, df, *, schema=None, table=None, **kwargs)`: Write hierarchy data to the specified database table.
- `dispose(self)`: Dispose of the SQLAlchemy engine.

## License

This package is licensed under the MIT License.
