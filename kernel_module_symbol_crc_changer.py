# Coded by Asderdd
import subprocess
import sys
from textwrap import wrap

def main(KERNEL_SYMVERS_FILE, INPUT_LIB_FILE, OUTPUT_LIB_FILE):
    
    # Parse the Module.symvers file
    def get_kernel_symvers(file):
        symbols = {}
        with open(file) as f:
            for i in f.readlines():
                symbols.update({i.split('\t')[1] : i.split('\t')[0]})
            return symbols

    # Convert hex string to little endian bytes
    def hex_to_little_byte(hex_str):
        little = ''
        for i in wrap(hex_str[2::], 2)[::-1]:
            little += i
        return bytes.fromhex(little)

    # Dump modversions of given kernel module and parse it to a dictionary
    def get_module_symvers(LIB_FILE):
        symbols = {}
        shell_output = subprocess.run('modprobe --dump-modversions ' + LIB_FILE, stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')
        for i in shell_output.splitlines():
            symbols.update({i.split('\t')[1].rstrip('\n') : i.split('\t')[0]})
        return symbols

    # Replace crc value of each symbol in kernel module with new values those taken from Module.symvers file
    def patch_lib(kernel_file, input_lib, output_lib):
        with open(input_lib, 'rb') as in_file, open(output_lib, 'wb') as out_file:
            filedata = in_file.read()
            kernel_symbols = get_kernel_symvers(kernel_file)
            mod_symbols = get_module_symvers(input_lib)
            success_count = 0
            for key, value in mod_symbols.items():
                try:
                    filedata = filedata.replace(hex_to_little_byte(value), hex_to_little_byte(kernel_symbols[key]))
                    print(key, 'symbol crc changed from', value, 'to', kernel_symbols[key] + '\n')
                    success_count += 1
                except KeyError:
                    print(key, 'is not found in Module.symvers file')
                    input('If you want to continue press ENTER . . .\n')
                    pass
            out_file.write(filedata)
            print(success_count, 'of', len(mod_symbols),'symbol crc values has been successfully changed.')
         

    patch_lib(KERNEL_SYMVERS_FILE, INPUT_LIB_FILE, OUTPUT_LIB_FILE)


if __name__ == '__main__':
    try:
        KERNEL_SYMVERS_FILE = str(sys.argv[1])
        INPUT_LIB_FILE = str(sys.argv[2])
    except IndexError:
        print('\nUsage: kernel_module_symbol_crc_changer.py <kernel_symvers_file> <input_lib> [output_lib]\n')
        print('    <kernel_symvers_file>: Module.symvers file from kernel output directory')
        print('    [output_lib]: output name of patched kernel module\n')
        try:
            input = raw_input
        except NameError: pass
        input('Press ENTER to exit...')
        sys.exit()

    try:
        OUTPUT_LIB_FILE = str(sys.argv[3])
    except IndexError:
        OUTPUT_LIB_FILE = INPUT_LIB_FILE.rstrip('.ko') + '_patched.ko'

    main(KERNEL_SYMVERS_FILE, INPUT_LIB_FILE, OUTPUT_LIB_FILE)
