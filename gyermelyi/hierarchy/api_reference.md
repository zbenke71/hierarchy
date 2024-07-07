# Hierarchy Package API Reference

## Class: `Hierarchy`

The `Hierarchy` class provides methods to create, manage, and manipulate hierarchical data structures from various sources including lists, tuples, pandas DataFrames, and Oracle databases.

### Initialization

```python
Hierarchy(source=None, config_file=None)
```

Initialize a `Hierarchy` object with source data or a configuration file.

- **Parameters:**
  - `source`: Optional. A list, tuple, or pandas DataFrame containing the source data. Each entry should represent a parent-child relationship.
  - `config_file`: Optional. Path to a configuration file containing database connection and source/destination settings.

### Methods

#### `create_hierarchy(self)`

Create the hierarchical structure from the source data.

- **Returns:** None

#### `delete_hierarchy(self)`

Delete the current hierarchy, setting it to None.

- **Returns:** None

#### `to_tuples(self, *, flattened=True, empty_value=None, has_primkey=True)`

Get the hierarchical structure as a set of tuples.

- **Parameters:**
  - `flattened`: Optional. If True, flatten the hierarchy. Default is True.
  - `empty_value`: Optional. The value to use for non-existing data when flattening the hierarchy.
  - `has_primkey`: Optional. A boolean indicating whether the output should include a primary key.

- **Returns:** Set of tuples representing the hierarchy.

#### `to_lists(self, *, flattened=True, empty_value=None, has_primkey=True)`

Get the hierarchical structure as a list of lists.

- **Parameters:**
  - `flattened`: Optional. If True, flatten the hierarchy. Default is True.
  - `empty_value`: Optional. The value to use for non-existing data when flattening the hierarchy.
  - `has_primkey`: Optional. A boolean indicating whether the output should include a primary key.

- **Returns:** List of lists representing the hierarchy.

#### `to_dataframe(self, *, empty_value=None, level_label=None, has_primkey=True, primkey_label=None)`

Convert the hierarchical structure into a pandas DataFrame.

- **Parameters:**
  - `empty_value`: Optional. The value to use for non-existing data when flattening the hierarchy.
  - `level_label`: Optional. The label to use for the level columns.
  - `has_primkey`: Optional. A boolean indicating whether the DataFrame should include a primary key column.
  - `primkey_label`: Optional. The label to use for the primary key column.

- **Returns:** A DataFrame containing the flattened hierarchy. Returns None if an error occurs.

#### `read_source_from_db(self)`

Read the source data from the database and update the source attribute.

- **Returns:** None

#### `to_database(self, *, empty_value=None, level_label=None, has_primkey=True, primkey_label=None, **kwargs)`

Write the hierarchy data to the database.

- **Parameters:**
  - `empty_value`: Optional. The value to use for non-existing data when flattening the hierarchy.
  - `level_label`: Optional. The label to use for the level columns.
  - `has_primkey`: Optional. A boolean indicating whether the DataFrame should include a primary key column.
  - `primkey_label`: Optional. The label to use for the primary key column.
  - `**kwargs`: Additional keyword arguments for database connection and table settings.

- **Returns:** None

### Example Usage

```python
from gyermelyi.hierarchy import Hierarchy

# Example source data
source = [['parent1', 'child1'], ['parent1', 'child2'], ['parent2', 'child3']]

# Initialize hierarchy from source data
hierarchy = Hierarchy(source=source)
hierarchy.create_hierarchy()

# Convert to DataFrame
df = hierarchy.to_dataframe(empty_value=None)
print(df)

# Write hierarchy to database
hierarchy.to_database()
```

## Configuration File

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

## Logging

The package uses the `logging` module to log errors and information. Ensure logging is configured in your application to capture these logs.
