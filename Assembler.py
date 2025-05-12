import sys
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

#Initializes instruction set architecture
instr = {
    "add": ("00000", 3), "addu": ("00000", 3), "addh": ("00000", 3),
    "sub": ("00001", 3), "subu": ("00001", 3), "subh": ("00001", 3),
    "mul": ("00010", 3), "mulu": ("00010", 3), "mulh": ("00010", 3),
    "div": ("00011", 3), "divu": ("00011", 3), "divh": ("00011", 3),
    "mod": ("00100", 3),
    "cmp": ("00101", 2),
    "and": ("00110", 3),
    "or": ("00111", 3),
    "not": ("01000", 2),
    "mov": ("01001", 2), "movu": ("01001", 2), "movh": ("01001", 2),
    "lsl": ("01010", 3),
    "lsr": ("01011", 3),
    "asr": ("01100", 3),
    "nop": ("01101", 0),
    "ld": ("01110", 3),
    "st": ("01111", 3),
    "beq": ("10000", 1),
    "bgt": ("10001", 1),
    "b": ("10010", 1),
    "call": ("10011", 1),
    "ret": ("10100", 0),
    "hlt": ("11111", 0)
}
labels = {}
filtered = []

#The table will store ASM code in the format given below
#Label | Mnemonic | Operand | true/false if label is present or not
class TableEntry:
    def __init__(self):
        self.label = ""
        self.instruction = ""
        self.operand = []
        self.labelPresent = False
parseTree = []      #Stores parsed code
machineCode = []    #Stores Machine Code
registers = {       #Map of registers
    "R0": "0000", "R1": "0001", "R2": "0010", "R3": "0011",
    "R4": "0100", "R5": "0101", "R6": "0110", "R7": "0111",
    "R8": "1000", "R9": "1001", "R10": "1010", "R11": "1011",
    "R12": "1100", "R13": "1101", "R14": "1110", "R15": "1111"
}

def generate_errors(line, message):
    messagebox.showerror("Error", f"{message} at line: {line}"
    )
    sys.exit(1)

def trim(s, line_num):  #Trims code and cleans spaces
    s = s.strip()
    temp = ""
    i = 0
    s_len = len(s)
    while i < s_len:
        if s[i] == ':':
            temp += ":"
            if i == s_len - 1 or s[i + 1] != ' ':
                temp += " "
            i += 1
            continue
        if s[i] == '/':
            break
        if s[i] != ' ' and s[i] != '\t':
            temp += s[i]
            i += 1
            continue
        temp += " "
        j = i
        while i < s_len and (s[i] == ' ' or s[i] == '\t'):
            i += 1
    while temp and (temp[-1] == '\t' or temp[-1] == ' '):
        temp = temp[:-1]
    return temp

def imm_to_binary(imm): #Converts immediate to binary
    if imm < -131072 or imm > 131071:
        messagebox.showerror("Error", "Immediate value out of range (-131072 to 131071)")
        sys.exit(1)
    if imm < 0:
        return bin(imm & 1111111111111111)[2:].zfill(16)
    else:
        return bin(imm)[2:].zfill(16)

def lexer(line):    #Lexer to divide code into tokens/lexemes
    return line.split()

def process_labels():
    #Stores labels in label map
    global labels
    labels = {}
    address = 0
    for line in filtered:
        tokens = lexer(line)
        if not tokens:
            continue
        if tokens[0].endswith(':'):
            label = tokens[0][:-1]
            labels[label] = address
        address += 4

def parser():
    #Parses entire code and checks syntax
    global parseTree
    parseTree = [TableEntry() for _ in range(len(filtered))]
    for i, line_str in enumerate(filtered):
        # print(line_str)
        line = lexer(line_str)
        # print(line)
        if not line:
            continue
        if line[0].endswith(':'):
            # print(line[0].endswith(':'))
            parseTree[i].label = line[0][:-1]
            parseTree[i].labelPresent = True
            if len(line) == 1:
                generate_errors(i + 1, "Only label present")
        else:
            parseTree[i].labelPresent = False
            parseTree[i].label = " "
            if line[0] in instr:
                parseTree[i].instruction = line[0]
            else:
                generate_errors(i + 1, "Invalid instruction")

        # operand_start_index = 1 if not parseTree[i].labelPresent else 2
        for j in range(1, len(line)):
            if j == 1:
                if parseTree[i].labelPresent:
                    if line[j] in instr:
                        parseTree[i].instruction = line[j]
                    else:
                        generate_errors(i + 1, "Invalid instruction")       #error 
                    continue
            if (j - (1 if not parseTree[i].labelPresent else 2) == 1) and (parseTree[i].instruction == "ld" or parseTree[i].instruction == "st"):
                parseTree[i].operand.append(line[j][-2:])
                parseTree[i].operand.append(line[j][:-3])
            else:
                parseTree[i].operand.append(line[j])

        if parseTree[i].instruction and instr[parseTree[i].instruction][1] != len(parseTree[i].operand):
            generate_errors(i + 1, "Invalid no. of operands")

def second_pass():
    global machineCode
    machineCode = []
    pc = 0
    for entry in parseTree:
        if not entry.instruction:
            continue
        binaryInstr = instr[entry.instruction][0]
        operandCount = instr[entry.instruction][1]
        binaryOperands = ""

        if operandCount > 1:
            checkImm = entry.operand[-1]
            if checkImm not in registers and checkImm not in labels:
                binaryInstr += "1"
            else:
                binaryInstr += "0"

        if instr[entry.instruction][1] > 1:
            if entry.instruction.endswith('u'):
                binaryInstr += "01"
            elif entry.instruction.endswith('h'):
                binaryInstr += "10"
            else:
                binaryInstr += "00"

        if operandCount == 0:
            binaryOperands += "0" * 27

        if entry.instruction == "cmp":
            binaryOperands += "0000"

        for i in range(operandCount):
            operand = entry.operand[i]
            if i == 1 and (entry.instruction == "not" or entry.instruction == "mov"):
                binaryOperands += "0000"
            if operand in registers:
                binaryOperands += registers[operand]
            elif operand in labels:
                address = labels[operand]
                if address-pc<0:
                    addrBits = bin((2**27)+((address - pc) // 4))[2:].zfill(27)
                else:
                    addrBits = bin((address - pc) // 4)[2:].zfill(27)
                binaryOperands += addrBits
            else:
                imm = int(operand)
                binaryOperands += imm_to_binary(imm)

        finalBinary = binaryInstr + binaryOperands
        while len(finalBinary) < 32:
            finalBinary += "0"
        machineCode.append(finalBinary)
        pc += 4

def first_pass():
    process_labels()
    parser()
    second_pass()

class AssemblerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Assembler")

        # Menu Bar
        menubar = tk.Menu(master)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.load_file)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=master.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        master.config(menu=menubar)

        # Text Area for Assembly Code
        self.assembly_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=60, height=20)
        self.assembly_text.pack(padx=10, pady=10)

        # Buttons
        self.assemble_button = tk.Button(master, text="Assemble", command=self.assemble)
        self.assemble_button.pack(pady=5)

        # Text Area for Machine Code
        self.machine_code_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=60, height=10)
        self.machine_code_text.pack(padx=10, pady=10)

    def load_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".asm",
                                               filetypes=[("Assembly files", "*.asm"),
                                                          ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    self.assembly_text.delete(1.0, tk.END)
                    self.assembly_text.insert(tk.END, file.read())
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")

    def assemble(self):
        global filtered
        filtered = []
        assembly_code = self.assembly_text.get(1.0, tk.END).splitlines()
        line_num = 0
        for line in assembly_code:
            line_num += 1
            cleaned_line = trim(line, line_num)
            if cleaned_line:
                filtered.append(cleaned_line)

        try:
            first_pass()
            self.machine_code_text.delete(1.0, tk.END)
            for code in machineCode:
                self.machine_code_text.insert(tk.END, code + "\n")
        except Exception as e:
            # Errors should be handled within the assembler functions, but this is a fallback
            messagebox.showerror("Error", f"An error occurred during assembly: {e}")
            self.machine_code_text.delete(1.0, tk.END)
            self.machine_code_text.insert(tk.END, "Assembly failed.")

if __name__ == "__main__":
    root = tk.Tk()
    gui = AssemblerGUI(root)
    root.mainloop()