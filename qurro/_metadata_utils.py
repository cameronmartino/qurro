#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Copyright (c) 2018--, Qurro development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# ----------------------------------------------------------------------------

import logging
import pandas as pd
import numpy as np
from io import StringIO


def ensure_df_headers_unique(df, df_name):
    """Raises an error if the index or columns of the DataFrame aren't unique.

       (If both index and columns are non-unique, the index error will take
       precedence.)

       If these fields are unique, no errors are raised and nothing (None) is
       implicitly returned.

       Parameters
       ----------

       df: pandas.DataFrame
       df_name: str
           The "name" of the DataFrame -- this is displayed to the user in the
           error message thrown if the DataFrame has any non-unique IDs.
    """
    if len(df.index.unique()) != df.shape[0]:
        raise ValueError(
            "Indices of the {} DataFrame are not" " unique.".format(df_name)
        )

    if len(df.columns.unique()) != df.shape[1]:
        raise ValueError(
            "Columns of the {} DataFrame are not" " unique.".format(df_name)
        )


def validate_df(df, name, min_row_ct, min_col_ct):
    """Does some basic validation on the DataFrame.

       1. Calls ensure_df_headers_unique() to ensure that index and column
          names are unique.
       2. Checks that the DataFrame has at least min_row_ct rows.
       3. Checks that the DataFrame has at least min_col_ct columns.
    """
    ensure_df_headers_unique(df, name)
    logging.debug("Ensured uniqueness of {}.".format(name))
    if df.shape[0] < min_row_ct:
        raise ValueError(
            "Less than {} rows found in the {}.".format(min_row_ct, name)
        )
    if df.shape[1] < min_col_ct:
        raise ValueError(
            "Less than {} columns found in the {}.".format(min_col_ct, name)
        )


def fix_id(fid):
    """As a temporary measure, escapes certain special characters in a name.

       Right now, a measure like this is required to make Vega* work properly
       with various field names.

       See https://github.com/vega/vega-lite/issues/4965.
    """

    new_id = ""
    for c in fid:
        if c == ".":
            new_id += ":"
        elif c == "]":
            new_id += ")"
        elif c == "[":
            new_id += "("
        elif c == "'" or c == '"' or c == "\\":
            new_id += "|"
        else:
            new_id += c
    return new_id


def get_q2_comment_lines(md_file_loc):
    """Returns a list of line numbers in the file that start with "#q2:".

       These lines should be skipped when parsing the file outside of Q2 (i.e.
       in pandas). I guess we could also ostensibly use these lines' types here
       eventually, but for now we just skip them.

       Notes:
        -The line numbers are 0-indexed (so they can easily be thrown in to
         pandas.read_csv() as the skiprows parameter)
        -This doesn't check check the first line of the file (assumed to be the
         header)
        -This stops checking lines once it gets to the first non-header line
         that doesn't start with "#q2:". Currently, "#q2:types" is the only Q2
         "comment directive" available, but ostensibly this could detect future
         Q2 comment directives.
        -This checks if md_file_loc is of type StringIO. If so, this will
         handle it properly (iterating over it directly); otherwise, this
         assumes that md_file_loc is an actual filename, and this will open
         it using open().
         (I realize that ideally this wouldn't have to do any type checking,
         but it's either this or do a bunch of weird refactoring to get my test
         code working.)
    """

    def iterate_over_file_obj_lines(file_obj):
        q2_lines = []
        line_num = 0
        for line in file_obj:
            # Don't check for a #q2: comment on the first line of the file,
            # since the first line (should) define the file header.
            if line_num > 0:
                if line.startswith("#q2:"):
                    q2_lines.append(line_num)
                else:
                    # We assume that all #q2: lines will occur at the start of
                    # the file. Once we've reached a line that doesn't start
                    # with "#q2:", we stop checking.
                    break
            line_num += 1
        return q2_lines

    if type(md_file_loc) == StringIO:
        q2_lines = iterate_over_file_obj_lines(md_file_loc)
        # HACK: Allow us to read through this StringIO again --
        # https://stackoverflow.com/a/27261215/10730311
        # Note that we're only ever bothering with StringIOs here during test
        # code, so this weirdness should be ignored during normal operation of
        # Qurro.
        md_file_loc.seek(0)
        return q2_lines
    else:
        with open(md_file_loc, "r") as md_file_obj:
            return iterate_over_file_obj_lines(md_file_obj)


def read_metadata_file(md_file_loc):
    """Reads in a metadata file using pandas.read_csv().

       This treats all metadata values (including the index column) as
       strings, due to the use of dtype=object.
    """
    q2_lines = get_q2_comment_lines(md_file_loc)
    metadata_df = pd.read_csv(
        md_file_loc,
        sep="\t",
        na_values=[""],
        keep_default_na=False,
        dtype=object,
        skiprows=q2_lines,
    )

    # Take care of leading/trailing whitespace
    for column in metadata_df.columns:
        # Strip surrounding whitespace from each value
        # This mimics how QIIME 2 ignores this whitespace
        metadata_df[column] = metadata_df[column].str.strip()
    # Sorta the opposite of replace_nan(). Find all of the ""s resulting from
    # removing values with just-whitespace, and convert them to NaNs.
    metadata_df.where(metadata_df != "", np.NaN, inplace=True)

    # If there are any NaNs in the first column (that will end up being the
    # index column), then the user supplied at least one empty ID
    # (remember that we just converted all ""s to NaNs).
    #
    # This is obviously terrible, so just raise an error (this sort of
    # situation also results in an error from qiime2.Metadata).
    if metadata_df[metadata_df.columns[0]].isna().any():
        raise ValueError("Empty ID found in metadata file.")

    # Instead of passing index_col=0 to pd.read_csv(), we delay setting the
    # first column as the index until after we've read in the metadata file.
    #
    # This is because, as of writing, pandas doesn't set the dtype of the
    # index_col (see https://stackoverflow.com/a/35058538/10730311 for a good
    # explanation) -- so if we don't delay setting the index column, then it
    # won't necessarily be read as an object dtype. This can have bad results
    # (e.g. the sample IDs start with 0s, and those 0s will be removed by
    # pandas).
    #
    # This workaround should address this.
    metadata_df.set_index(metadata_df.columns[0], inplace=True)
    return metadata_df


def replace_nan(df, new_nan_val=None):
    """Replaces all occurrences of NaN values in the DataFrame with a specified
       value.

       Note that this solution seems to result in the DataFrame's columns'
       dtypes being changed to object. (This shouldn't change much due to how
       we handle metadata files, though.)

       Based on the solution described here:
       https://stackoverflow.com/a/14163209/10730311
    """
    return df.where(df.notna(), new_nan_val)


def escape_columns(df):
    """Calls fix_id() on each of the column names of the DF."""
    new_cols = []
    for col in df.columns:
        new_cols.append(fix_id(col))
    df.columns = new_cols
    # Ensure that this didn't make the column names non-unique
    ensure_df_headers_unique(df, "escape_columns() DataFrame")
    return df


def get_truncated_feature_id(full_feature_id):
    """Computes a truncated GNPS feature ID from a full GNPS feature ID.

       This function was originally contained in a Jupyter Notebook for
       processing this sort of data written by Jamie Morton and
       Julia Gauglitz.
    """
    mz, rt = list(map(float, full_feature_id.split(";")))
    return "{:.4f};{:.4f}".format(mz, rt)


def read_gnps_feature_metadata_file(md_file_loc, feature_ranks_df):
    """Reads in a GNPS feature metadata file, producing a sane DataFrame.

       Also requires a DataFrame describing feature ranks as input. This is so
       that we can match up the feature rank IDs in the ranks and BIOM table
       with rows in the GNPS metadata file -- the precision of the numbers from
       which GNPS feature IDs are computed varies between the ranks/BIOM table
       and the actual numbers contained in the GNPS metadata file.
    """
    # Note that we don't set index_col = 0 -- the columns we care about
    # ("parent mass", "RTConsensus", and "LibraryID"), as far as I know, don't
    # have a set position. So we'll just use the basic RangeIndex that pandas
    # defaults to.
    q2_lines = get_q2_comment_lines(md_file_loc)
    metadata_df = pd.read_csv(
        md_file_loc, sep="\t", na_filter=False, skiprows=q2_lines
    )

    # Create a feature ID column from the parent mass and RTConsensus cols.
    # Use of .map() here is derived from
    # https://stackoverflow.com/a/22276757/10730311.
    metadata_df["qurro_trunc_feature_id"] = (
        metadata_df["parent mass"].map("{:.4f}".format)
        + ";"
        + metadata_df["RTConsensus"].map("{:.4f}".format)
    )

    # Go through feature rank index, and for each create a mapping of
    # (truncated feature ID) -> (full feature ID). Then use that mapping to
    # create a new column of "qurro_full_feature_id" in metadata_df.
    # NOTE that if there are indistinguishable truncated IDs, this will raise
    # an error.
    truncated_id_to_full_id = {}
    for fid in feature_ranks_df.index:
        tfid = get_truncated_feature_id(fid)
        if tfid not in truncated_id_to_full_id:
            truncated_id_to_full_id[tfid] = fid
        else:
            logging.warning(
                "Indistinguishable rows in GNPS feature "
                "metadata file with truncated ID {}.".format(tfid)
            )
            # Replace the full feature ID with a bogus ID. This will prevent
            # the >= 2 full feature IDs from which the conflicting truncated
            # IDs were derived from getting annotated with anything -- better
            # to annotate less than to annotate incorrectly.
            truncated_id_to_full_id[tfid] = "qurro_matching_conflict"

    metadata_df["qurro_full_feature_id"] = metadata_df[
        "qurro_trunc_feature_id"
    ].apply(lambda tfid: truncated_id_to_full_id[tfid])

    # Remove all rows in the metadata df with bogus full feature IDs,
    # which will let us use verify_integrity=True when setting index below.
    # There's definitely a faster way to do this than using iterrows(), but
    # this at least works
    indices_to_remove = []
    for idx, row in metadata_df.iterrows():
        if row["qurro_full_feature_id"] == "qurro_matching_conflict":
            indices_to_remove.append(idx)

    metadata_df.drop(index=indices_to_remove, inplace=True)

    # Set the full feature ID column as the actual index of the DataFrame. If
    # there are any duplicates (due to two features having the same
    # mass-to-charge ratio and discharge time), our use of verify_integrity
    # here will raise an error accordingly. (That almost certainly won't
    # happen, # since we already look for indistinguishable truncated feature
    # IDs above, but best to be safe until this function is more rigorously
    # tested.)
    metadata_df.set_index(
        "qurro_full_feature_id", verify_integrity=True, inplace=True
    )

    # Remove all the feature metadata that we don't care about (now, at least).
    # metadata_df now only contains the full feature ID we constructed and the
    # Library ID, so now it's ready to be used to annotate feature IDs from teh
    # ranks DataFrame.
    metadata_df = metadata_df.filter(items=["LibraryID"])
    return metadata_df
