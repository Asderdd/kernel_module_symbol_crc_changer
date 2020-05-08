This program changes symbol crc values of precompiled kernel modules to use with another kernel that doesn't has same header.



Usage: kernel_module_symbol_crc_changer.py <kernel_symvers_file> <input_lib> [output_lib]

    <kernel_symvers_file>: Module.symvers file from kernel output directory
    [output_lib]: output name of patched kernel module
