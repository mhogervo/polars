from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Iterable

from polars.datatypes import is_polars_dtype
from polars.utils._wrap import wrap_expr

with contextlib.suppress(ImportError):  # Module not available when building docs
    import polars.polars as plr

if TYPE_CHECKING:
    from polars import Expr
    from polars.type_aliases import PolarsDataType

__all__ = ["col"]


class ColumnFactory:
    """
    Helper class for creating column expressions.

    An instance of this class is exported under the name ``col``. It can be used as
    though it were a function by calling, for example, ``pl.col("foo")``.
    See the :func:`__call__` method for further documentation.

    This helper class enables an alternative syntax for creating a column expression
    through attribute lookup. For example ``col.foo`` creates an expression equal to
    ``col("foo")``.
    See the :func:`__getattr__` method for further documentation.

    Notes
    -----
    The function call syntax is considered the idiomatic way of constructing a column
    expression. The alternative attribute syntax can be useful for quick prototyping as
    it can save some keystrokes, but has drawbacks in both expressiveness and
    readability.

    """

    def __call__(
        self,
        name: str | PolarsDataType | Iterable[str] | Iterable[PolarsDataType],
        *more_names: str | PolarsDataType,
    ) -> Expr:
        """
        Create a column expression representing column(s) in a dataframe.

        Parameters
        ----------
        name
            The name or datatype of the column(s) to represent.
            Accepts regular expression input.
            Regular expressions should start with ``^`` and end with ``$``.
        *more_names
            Additional names or datatypes of columns to represent,
            specified as positional arguments.

        Examples
        --------
        Pass a single column name to represent that column.

        >>> df = pl.DataFrame(
        ...     {
        ...         "ham": [1, 2],
        ...         "hamburger": [11, 22],
        ...         "foo": [2, 1],
        ...         "bar": ["a", "b"],
        ...     }
        ... )
        >>> df.select(pl.col("foo"))
        shape: (2, 1)
        ┌─────┐
        │ foo │
        │ --- │
        │ i64 │
        ╞═════╡
        │ 2   │
        │ 1   │
        └─────┘

        Use dot syntax to save keystrokes for quick prototyping.

        >>> from polars import col as c
        >>> df.select(c.foo + c.ham)
        shape: (2, 1)
        ┌─────┐
        │ foo │
        │ --- │
        │ i64 │
        ╞═════╡
        │ 3   │
        │ 3   │
        └─────┘

        Use the wildcard ``*`` to represent all columns.

        >>> df.select(pl.col("*"))
        shape: (2, 4)
        ┌─────┬───────────┬─────┬─────┐
        │ ham ┆ hamburger ┆ foo ┆ bar │
        │ --- ┆ ---       ┆ --- ┆ --- │
        │ i64 ┆ i64       ┆ i64 ┆ str │
        ╞═════╪═══════════╪═════╪═════╡
        │ 1   ┆ 11        ┆ 2   ┆ a   │
        │ 2   ┆ 22        ┆ 1   ┆ b   │
        └─────┴───────────┴─────┴─────┘
        >>> df.select(pl.col("*").exclude("ham"))
        shape: (2, 3)
        ┌───────────┬─────┬─────┐
        │ hamburger ┆ foo ┆ bar │
        │ ---       ┆ --- ┆ --- │
        │ i64       ┆ i64 ┆ str │
        ╞═══════════╪═════╪═════╡
        │ 11        ┆ 2   ┆ a   │
        │ 22        ┆ 1   ┆ b   │
        └───────────┴─────┴─────┘

        Regular expression input is supported.

        >>> df.select(pl.col("^ham.*$"))
        shape: (2, 2)
        ┌─────┬───────────┐
        │ ham ┆ hamburger │
        │ --- ┆ ---       │
        │ i64 ┆ i64       │
        ╞═════╪═══════════╡
        │ 1   ┆ 11        │
        │ 2   ┆ 22        │
        └─────┴───────────┘

        Multiple columns can be represented by passing a list of names.

        >>> df.select(pl.col(["hamburger", "foo"]))
        shape: (2, 2)
        ┌───────────┬─────┐
        │ hamburger ┆ foo │
        │ ---       ┆ --- │
        │ i64       ┆ i64 │
        ╞═══════════╪═════╡
        │ 11        ┆ 2   │
        │ 22        ┆ 1   │
        └───────────┴─────┘

        Or use positional arguments to represent multiple columns in the same way.

        >>> df.select(pl.col("hamburger", "foo"))
        shape: (2, 2)
        ┌───────────┬─────┐
        │ hamburger ┆ foo │
        │ ---       ┆ --- │
        │ i64       ┆ i64 │
        ╞═══════════╪═════╡
        │ 11        ┆ 2   │
        │ 22        ┆ 1   │
        └───────────┴─────┘

        Easily select all columns that match a certain data type by passing that
        datatype.

        >>> df.select(pl.col(pl.Utf8))
        shape: (2, 1)
        ┌─────┐
        │ bar │
        │ --- │
        │ str │
        ╞═════╡
        │ a   │
        │ b   │
        └─────┘
        >>> df.select(pl.col(pl.Int64, pl.Float64))
        shape: (2, 3)
        ┌─────┬───────────┬─────┐
        │ ham ┆ hamburger ┆ foo │
        │ --- ┆ ---       ┆ --- │
        │ i64 ┆ i64       ┆ i64 │
        ╞═════╪═══════════╪═════╡
        │ 1   ┆ 11        ┆ 2   │
        │ 2   ┆ 22        ┆ 1   │
        └─────┴───────────┴─────┘


        """
        if more_names:
            if isinstance(name, str):
                names_str = [name]
                names_str.extend(more_names)  # type: ignore[arg-type]
                return wrap_expr(plr.cols(names_str))
            elif is_polars_dtype(name):
                dtypes = [name]
                dtypes.extend(more_names)
                return wrap_expr(plr.dtype_cols(dtypes))
            else:
                raise TypeError(
                    "invalid input for `col`"
                    f"\n\nExpected `str` or `DataType`, got {type(name).__name__!r}."
                )

        if isinstance(name, str):
            return wrap_expr(plr.col(name))
        elif is_polars_dtype(name):
            return wrap_expr(plr.dtype_cols([name]))
        elif isinstance(name, Iterable):
            names = list(name)
            if not names:
                return wrap_expr(plr.cols(names))

            item = names[0]
            if isinstance(item, str):
                return wrap_expr(plr.cols(names))
            elif is_polars_dtype(item):
                return wrap_expr(plr.dtype_cols(names))
            else:
                raise TypeError(
                    "invalid input for `col`"
                    "\n\nExpected iterable of type `str` or `DataType`,"
                    f" got iterable of type {type(item).__name__!r}"
                )
        else:
            raise TypeError(
                "invalid input for `col`"
                f"\n\nExpected `str` or `DataType`, got {type(name).__name__!r}"
            )

    def __getattr__(self, name: str) -> Expr:
        """
        Create a column expression using attribute syntax.

        Note that this syntax does not support passing data types or multiple column
        names.

        Parameters
        ----------
        name
            The name of the column to represent.

        Examples
        --------
        >>> from polars import col as c
        >>> df = pl.DataFrame(
        ...     {
        ...         "foo": [1, 2],
        ...         "bar": [3, 4],
        ...     }
        ... )
        >>> df.select(c.foo + c.bar)
        shape: (2, 1)
        ┌─────┐
        │ foo │
        │ --- │
        │ i64 │
        ╞═════╡
        │ 4   │
        │ 6   │
        └─────┘

        """
        return wrap_expr(plr.col(name))


# Set up a single instance of the class and use it as a column factory
col = ColumnFactory()