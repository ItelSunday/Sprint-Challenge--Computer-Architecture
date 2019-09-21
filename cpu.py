"""CPU functionality."""
#MDR = Memory Data Register | MAR = Memory Address Register

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # Memory to hold 256 bytes of memory
        self.ram = [00000000] * 256
        # registers
        self.reg = [0] * 8
        self.fl = None
        #initialize start of stack points into memory, store in r7
        self.sp = 0xF4
        self.reg[7] = self.ram[self.sp]

        # initialize pc to increment
        self.pc = 0
        
         #initialize branch table with all opcodes and the function call
        self.branch_table = {}
        self.branch_table[0b10000010] = self.handle_ldi
        self.branch_table[0b01000111] = self.handle_prn
        self.branch_table[0b00000001] = self.handle_hlt
        self.branch_table[0b01000101] = self.handle_push
        self.branch_table[0b01000110] = self.handle_pop
        self.branch_table[0b00010001] = self.handle_ret
        self.branch_table[0b01010000] = self.handle_call
        self.branch_table[0b01010100] = self.handle_jmp
        self.branch_table[0b01010101] = self.handle_jeq
        self.branch_table[0b01010110] = self.handle_jne
       
    def ram_read(self, MAR):
        #accepts the address to read and return the value
        return self.ram[MAR]

    def ram_write(self, MDR, MAR):
        #accepts a value to write, and the adrress to write it to
        self.ram[MAR] = MDR

    def load(self):
        """Load a program into memory."""
        address = 0

        if len(sys.argv) != 2:
            print(f'usage: {sys.argv[0]} [file]')
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    #find first part of instruction
                    number = line.split('#')[0]
                    #replace all \n with empty space
                    number = number.replace('\n', '')
                    #remove any empty space 
                    number = number.strip()

                    #convert binary to int and store in ram
                    if number is not '':
                        number = int(number, 2)
                        # add to the memory
                        self.ram[address] = number
                        address += 1

        except FileNotFoundError:
            print(f'{sys.argv[0]}: File not found')
            sys.exit(2)


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        #operation handled within ALU
        MUL = 0b10100010
        ADD = 0b10100000
        SUB = 0b10100001
        DIV = 0b10100011
        XOR = 0b10101011
        SHR = 0b10101101
        SHL = 0b10101100
        CMP = 0b10100111
        AND = 0b10101000
        OR = 0b10101010
        NOT = 0b01101001
        MOD = 0b10100100

        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif op == SUB:
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == DIV:
            if not self.reg[reg_b]:
                print("Error: You are not allowed to divide a number by 0.")
                sys.exit()
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == CMP:
            if self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            elif self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
        elif op == AND:
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]
        elif op == OR:
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]
        elif op == XOR:
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]
        elif op == NOT:
            self.reg[reg_a] = ~self.reg[reg_a]
        elif op == SHL:
            self.reg[reg_a] = self.reg[reg_a] << self.reg[reg_b]
        elif op == SHR:
            self.reg[reg_a] = self.reg[reg_a] >> self.reg[reg_b]
        elif op == MOD:
            self.reg[reg_a] = self.reg[reg_a] % self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")
        self.pc += 3

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def handle_ldi(self, operand_a, operand_b):
        #LDI opcode, store vlaue at register
        self.reg[operand_a] = operand_b
        self.pc += 3

    def handle_prn(self, operand_a):
        print(self.reg[operand_a])
        self.pc += 2

    def handle_hlt(self):
        print('code halting...')
        sys.exit()

    def handle_push(self, operand_a):
        #decrement then store in the stack
        self.sp -= 1
        r_value = self.reg[operand_a]
        self.ram[self.sp] = r_value
        self.pc += 2

    def handle_pop(self, operand_a):
        #store value in stack indicated by pointer, store in register at given reg index given by operand
        value = self.ram[self.sp]
        self.reg[operand_a] = value
        self.sp += 1
        self.pc += 2

    def handle_ret(self):
        #pop from top of the stack
        ret_address = self.ram[self.sp]
        self.pc = ret_address

    def handle_call(self, operand_a):
        #call function at the register
        self.sp -= 1
        call_address = self.pc + 2
        self.ram[self.sp] = call_address
        register_ram = self.ram[self.pc + 1]
        sub_address = self.reg[register_ram]
        self.pc = sub_address

    def handle_jmp(self, operand_a):
        self.pc = self.reg[operand_a]

    def handle_jeq(self, operand_a):
        if self.fl == 0b00000001:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2

    def handle_jne(self, operand_a):
        if self.fl != 0b00000001:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2

    def run(self):
        """Run the CPU."""

        while True:
            #hold a copy of the currently executing 8-bit instruction
            ir = self.ram[self.pc]

            #stores operands a and b which can be 1 or 2 bytes ahead of instruction byte, or nonexistent
            operand_a = self.ram_read(self.pc+1)
            operand_b = self.ram_read(self.pc+2)

            # mask and shift to determiner number of operands
            num_operands  = (ir & 0b11000000) >> 6
            alu_handle = (ir & 0b00100000) >> 5

            if alu_handle == 1:
                self.alu(ir, operand_a, operand_b)

            elif num_operands == 2:
                self.branch_table[ir](operand_a, operand_b)
            elif num_operands == 1:
                self.branch_table[ir](operand_a)
            elif num_operands == 0:
                self.branch_table[ir]()
            else:
                self.handle_hlt()
