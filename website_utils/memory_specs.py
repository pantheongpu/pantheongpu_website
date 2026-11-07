"""Memory type of a GPU product, for results whose report did not carry one.

Pantheon reads a card's memory type from the driver. Releases before 1.2.1 did not
read it at all, NVIDIA drivers older than 580 refuse the request Pantheon 1.2.4 sends
(each driver wants its own request size), and a card behind WSL has no driver device
to ask. For those results the published type read N/A even though every one of these
products has exactly one memory type.

This table fills the gap, and only the gap: a type the driver reported always wins.
It is keyed by the exact model name a report publishes, because a model name that
spans memory types (a laptop and a desktop part sharing a name, say) must not be
here at all. Every entry is the type on the manufacturer's specification sheet.

What it does NOT do: the memory *vendor* (Samsung, SK hynix, Micron) is a property of
the individual board, not of the product, so it is never filled in from here and stays
N/A when the driver did not report it.

The driver reports a generation, not a marketing name: it says HBM2 for an HBM2e stack
and HBM3 for HBM3e. A row that was measured can therefore read "HBM2" where this table
says "HBM2e". Rows filled from this table carry ``memory_type_source`` so the two are
never confused.
"""

SPEC_SOURCE = "specification"

SPEC_MEMORY_TYPES = {
    # NVIDIA data centre, HBM
    "NVIDIA B200": "HBM3e",
    "NVIDIA GH200 480GB": "HBM3",  # the 96 GB HBM3 part; the 144 GB part is named "GH200 144G HBM3e"
    "NVIDIA H100 80GB HBM3": "HBM3",
    "NVIDIA H100 PCIe": "HBM2e",
    "NVIDIA A100-SXM4-80GB": "HBM2e",
    "NVIDIA A100-SXM4-40GB": "HBM2",
    "Tesla V100-SXM2-32GB": "HBM2",
    # NVIDIA data centre and workstation, GDDR
    "NVIDIA A10": "GDDR6",
    "NVIDIA A10G": "GDDR6",
    "NVIDIA A40": "GDDR6",
    "NVIDIA L4": "GDDR6",
    "NVIDIA L40S": "GDDR6",
    "Tesla T4": "GDDR6",
    "NVIDIA T4G": "GDDR6",
    "NVIDIA RTX A4000": "GDDR6",
    "NVIDIA RTX A6000": "GDDR6",
    "NVIDIA RTX 4000 Ada Generation": "GDDR6",
    "NVIDIA RTX PRO 4500 Blackwell Server Edition": "GDDR7",
    "NVIDIA RTX PRO 6000 Blackwell Server Edition": "GDDR7",
    # NVIDIA GeForce
    "NVIDIA GeForce RTX 3060": "GDDR6",
    "NVIDIA GeForce RTX 3080 Ti": "GDDR6X",
    "NVIDIA GeForce RTX 4080 SUPER": "GDDR6X",
    "NVIDIA GeForce RTX 4090": "GDDR6X",
    "NVIDIA GeForce RTX 5090": "GDDR7",
    # AMD Radeon
    "AMD Radeon RX 6700 XT": "GDDR6",
    "AMD Radeon RX 6800": "GDDR6",
}

_BY_KEY = {" ".join(name.split()).casefold(): kind for name, kind in SPEC_MEMORY_TYPES.items()}


def spec_memory_type(gpu_name):
    """The specification's memory type for this model name, or None when it is not listed."""
    return _BY_KEY.get(" ".join(str(gpu_name or "").split()).casefold())
