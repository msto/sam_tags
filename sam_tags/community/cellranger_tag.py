from enum import StrEnum

from sam_tags import sam_tag


@sam_tag(strict=False, permit_standard_tag_collisions=True)
class CellrangerTag(StrEnum):
    """
    CellRanger-specific optional fields.

    https://www.10xgenomics.com/support/software/cell-ranger/latest/analysis/outputs/cr-outputs-bam
    """

    CB = "CB"
    """
    Chromium cellular barcode sequence that is error-corrected and confirmed against a list of
    known-good barcode sequences.

    For multiplex Fixed RNA Profiling, the cellular barcode is a combination of the 10x GEM Barcode
    and Probe Barcode sequences.
    """

    CR = "CR"
    """
    Chromium cellular barcode sequence as reported by the sequencer.

    For multiplex Fixed RNA Profiling, the cellular barcode is a combination of the 10x GEM Barcode
    and Probe Barcode sequences.
    """

    CY = "CY"
    """
    Chromium cellular barcode read quality.

    For multiplex Fixed RNA Profiling, the cellular barcode is a combination of the 10x GEM Barcode
    and Probe Barcode sequences. Phred scores as reported by sequencer.
    """

    UB = "UB"
    """
    Chromium molecular barcode sequence that is error-corrected among other molecular barcodes with
    the same cellular barcode and gene alignment.
    """

    UR = "UR"
    """
    Chromium molecular barcode sequence as reported by the sequencer.
    """

    UY = "UY"
    """
    Chromium molecular barcode read quality. Phred scores as reported by sequencer.
    """

    TR = "TR"
    """
    Trimmed sequence.

    For the Single Cell 3' v1 chemistry, this is trailing sequence following the UMI on Read 2. For
    the Single Cell 3' v2 chemistry, this is trailing sequence following the cell and molecular
    barcodes on Read 1.
    """

    RG = "RG"
    """Identifies the read group, indicating the library source of each read."""
