from collections import defaultdict
import logging
import pandas as pd
from bennet.config import Config
from .hierarchydb import HierarchyDBOracle

logger = logging.getLogger(__name__)


class Hierarchy:
    """
    A class to represent a hierarchical structure based on parent-child relationships.

    :ivar source: A list of lists or a pandas DataFrame where each sublist or row contains a parent-child pair.
    :ivar hierarchy: A set to store hierarchical paths.
    :ivar level: The prefix for level column names in the flattened hierarchy.
    :ivar primkey: The name for the primary key column in the flattened hierarchy.
    :ivar parent_map: A dictionary mapping each parent to its children.
    :ivar child_map: A dictionary mapping each child to its parents.
    """

    def __init__(self, source: list | tuple | pd.DataFrame = None, config_file=None):
        """
        Initialize the Hierarchy object with source data or a configuration file.

        :param source: A list of lists, tuple of tuples, or a pandas DataFrame where each sublist contains a parent-child pair.
        :param config_file: Path to the configuration file for database connection.
        """
        self.hierarchy = None
        self.source = None
        self.metadata = None
        self.hierarchydb = None

        self._validate(source, config_file)

        self.level = 'LVL'
        self.primkey = 'PK'

        self.parent_map = defaultdict(set)
        self.child_map = defaultdict(set)

    def _validate(self, source, config_file):
        """
        Validate the source data and the config_file for the hierarchy.

        :param source: Source data for the hierarchy, either as a list, tuple, or DataFrame.
        :param config_file: Path to the configuration file containing database connection settings.
        :raises TypeError: If the source is not a list of lists, tuple of tuples, or a pandas DataFrame.
        :raises ValueError: If the source list or tuple does not contain lists of exactly two elements or the DataFrame does not have exactly two columns.
        """
        try:
            if source is not None:
                if not isinstance(source, (list, tuple, pd.DataFrame)):
                    raise TypeError("The `source` must be a list of lists, tuple of tuples, or a pandas DataFrame")

                if isinstance(source, (list, tuple)):
                    if not all(isinstance(pair, (list, tuple)) and len(pair) == 2 for pair in source):
                        raise ValueError("The `source` list or tuple must contain lists or tuples of exactly two elements")

                if isinstance(source, pd.DataFrame):
                    if source.shape[1] != 2:
                        raise ValueError("DataFrame must have exactly two columns")
                self.source = source

            if config_file is not None:
                try:
                    self.metadata = Config(config_file)
                    self.hierarchydb = HierarchyDBOracle(**self.metadata.to_dict('database'))  # FIXME: NoneType as parameter
                except Exception:
                    raise TypeError("Failed to create the hierarchydb attribute")

            if self.source is None and self.hierarchydb is not None:
                self.read_source_from_db()

        except Exception as e:
            logger.error(f"Validation error: {e}")
            raise

    def _create_mapping(self):
        """
        Create parent-child mappings from the source data.
        """
        if isinstance(self.source, pd.DataFrame):
            for _, row in self.source.iterrows():
                parent, child = row
                if parent != child:
                    self.parent_map[parent].add(child)
                    self.child_map[child].add(parent)
                else:
                    self.parent_map[parent]
        else:
            for parent, child in self.source:
                if parent != child:
                    self.parent_map[parent].add(child)
                    self.child_map[child].add(parent)
                else:
                    self.parent_map[parent]

    def _find_root(self, node):
        """
        Find the root node of a given node by tracing its parents.

        :param node: The node for which to find the root.
        :return: The root node.
        """
        while node in self.child_map:
            node = next(iter(self.child_map[node]))
        return node

    def _build_path(self, node, path: list):
        """
        Recursively build hierarchical paths from the given node.

        :param node: The starting node for building the path.
        :param path: The current path being built.
        """
        path.append(node)
        if node not in self.parent_map or not self.parent_map[node]:  # is not a parent or its value is an empty set
            self.hierarchy.add(tuple(path))
        else:
            for child in self.parent_map[node]:
                self.hierarchy.add(tuple(path))
                self._build_path(child, path.copy())

    def create_hierarchy(self):
        """
        Create the hierarchical structure from the source data.
        """
        self.hierarchy = set()

        if self.source is not None:
            self._create_mapping()
            roots = {self._find_root(parent) for parent in self.parent_map.keys()}
            for root in roots:
                self._build_path(root, [])
            logger.info("Successfully created hierarchy.")
        else:
            logger.warning("Failed to create the hierarchy. The source attribute is None.")

    def delete_hierarchy(self):
        """
        Delete the current hierarchy, setting it to None.
        This method resets the hierarchy attribute to None, effectively deleting the current hierarchical structure.
        """
        self.hierarchy = None

    def _flatten_hierarchy(self, *args):
        """
        Flatten the hierarchical structure into a list of tuples.

        :param args: 
            The first argument is the value to be used for filling missing elements.
            The second argument is a boolean flag. If True, the last element of each tuple is appended to the end. If False, the last element is not appended.
        :return: A list of flattened tuples, each of the same length.
        """
        max_length = max(len(lst) for lst in self.hierarchy)
        flattened_data = []
        for lst in self.hierarchy:
            flattened_data.append(lst + tuple([args[0]] * (max_length - len(lst))) + lst[-1:None if args[1] else 0])
        return flattened_data

    def to_tuples(self, *, flattened=True, empty_value=None, has_primkey=True) -> set[tuple] | None:
        """
        Get the hierarchical structure as a set of tuples.

        :return: The hierarchical paths.
        """
        if self.hierarchy is None:
            self.create_hierarchy()

        try:
            return set(self._flatten_hierarchy(empty_value, has_primkey)) if flattened else self.hierarchy
        except Exception as e:
            logger.error(f"Failed to get the hierarchy as a set of tuples: {e}")
            return None

    def to_lists(self, *, flattened=True, empty_value=None, has_primkey=True) -> list[list] | None:
        """
        Get the hierarchical structure as a list of lists.

        :return: The hierarchical paths.
        """
        if self.hierarchy is None:
            self.create_hierarchy()

        try:
            return [list(path) for path in (self._flatten_hierarchy(empty_value, has_primkey) if flattened else self.hierarchy)]
        except Exception as e:
            logger.error(f"Failed to get the hierarchy as a list of lists: {e}")
            return None

    def to_dataframe(self, *, empty_value: int | str = None, level_label=None, has_primkey=True, primkey_label=None) -> pd.DataFrame | None:
        """
        Convert the hierarchical structure into a pandas DataFrame.

        :param empty_value: The value of the non-existing data.
        :param level_label: The label to use for the level columns. If not provided, the default level label is used.
        :param has_primkey: A boolean indicating whether the DataFrame should include a primary key column.
        :param primkey_label: The label to use for the primary key column. If not provided, the default primary key label is used.
        :return: A DataFrame containing the flattened hierarchy. Returns None if an error occurs.
        """
        if self.hierarchy is None:
            self.create_hierarchy()

        try:
            max_length = max(len(lst) for lst in self.hierarchy)
            return pd.DataFrame(self._flatten_hierarchy(empty_value, has_primkey),
                                columns=[f"{level_label or self.level}{i + 1:02d}" for i in range(max_length)] + [primkey_label or self.primkey])
        except Exception as e:
            logger.error(f"Failed to get the hierarchy as a pandas DataFrame: {e}")
            return None

    def read_source_from_db(self):
        """
        Read the source data from the database and updates the source attribute.

        :raises Exception: If there is an issue reading data from the database.
        """
        if self.hierarchydb is not None:
            data = self.hierarchydb.read_data(**self.metadata.to_dict('source'))
            if data is not None:
                self.source = data
                logger.info("Data retrieval successful. The source attribute has been updated.")
            else:
                logger.warning("Data retrieval failed. The source attribute remains unchanged.")

    def to_database(self, *, empty_value: int | str = None, level_label=None, has_primkey=True, primkey_label=None, **kwargs):
        """
        Write the hierarchy data to the database.

        :raises Exception: If there is an issue writing the hierarchy to the database.
        """
        if self.hierarchy is None:
            self.create_hierarchy()

        try:
            self.hierarchydb.write_data(
                self.to_dataframe(
                    empty_value=empty_value,
                    level_label=level_label or self.metadata.get('destination', 'level'),
                    has_primkey=has_primkey,
                    primkey_label=primkey_label or self.metadata.get('destination', 'primkey')),
                **self.metadata.to_dict('destination'),
                **kwargs)

            table = self.metadata.get('destination', 'table')
            schema = self.metadata.get('destination', 'schema')
            logger.info(f"Successfully wrote hierarchy to database table '{table}' in schema '{schema}'.")
        except Exception as e:
            logger.error(f"Failed to write hierarchy to database: {e}")
