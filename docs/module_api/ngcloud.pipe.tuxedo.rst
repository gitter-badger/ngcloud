Tuxedo pipeline
===============

.. py:currentmodule:: ngcloud.pipe.tuxedo

.. automodule:: ngcloud.pipe.tuxedo
    :no-members:
    :no-undoc-members:

.. autoclass:: TuxedoReport
    :show-inheritance:

.. autoclass:: IndexStage
    :show-inheritance:

.. autoclass:: QCStage
    :show-inheritance:

.. autoclass:: TophatStage
    :show-inheritance:


Helper classes:
---------------

.. autoclass:: TuxedoBaseStage

.. class:: OverSeq(seq, count, percentage, possible_source)

    Object to store over-represented sequence from FastQC.

    Generated from :py:func:`collections.namedtuple`,
    its attributes are *read-only*.

    Attributes
    ----------
    seq : str
        Over-represented sequence
    count : str
        Count of the over-rep sequence during sampling
    percentage : str
        Percentage of the sequencing during sampling.
        Value ranges [0, 100]
    possible_source : str
        Possilbe source of this over-rep(pollutant) sequence
        from FastQC database

