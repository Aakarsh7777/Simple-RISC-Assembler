#include <bits/stdc++.h>
using namespace std;

unordered_map<string,pair<string,int>> instr;                         //Map to store instructions
unordered_map<string,int> labels;                                     //Map to store labels
vector<string> filtered;                                              //Stores filtered code after cleaning spaces
// The table will store ASM code in the format given below
//  Label | Mnemonic | Operand | true/false if label is present or not
struct table{                                                         
    string label;
    string instruction;
    vector<string> operand;
    bool labelPresent;
};
vector<table> parseTree(100);                                         //Stores parsed code
vector<string> machineCode;                                           //Stores Machine Code
unordered_map<string,string> registers={                              //Map of registers
    {"R0","0000"},{"R1","0001"},{"R2","0010"},{"R3","0011"},
    {"R4","0100"},{"R5","0101"},{"R6","0110"},{"R7","0111"},
    {"R8","1000"},{"R9","1001"},{"R10","1010"},{"R11","1011"},
    {"R12","1100"},{"R13","1101"},{"R14","1110"},{"R15","1111"}
};
void ISA(){                                                           //Initializes instruction set architecture
    instr["add"]={"00000",3};
    instr["addu"]={"00000",3};
    instr["addh"]={"00000",3};
    instr["sub"]={"00001",3};
    instr["subu"]={"00001",3};
    instr["subh"]={"00001",3};
    instr["mul"]={"00010",3};
    instr["mulu"]={"00010",3};
    instr["mulh"]={"00010",3};
    instr["div"]={"00011",3};
    instr["divu"]={"00011",3};
    instr["divh"]={"00011",3};
    instr["mod"]={"00100",3};
    instr["cmp"]={"00101",2};
    instr["and"]={"00110",3};
    instr["or"]={"00111",3};
    instr["not"]={"01000",2};
    instr["mov"]={"01001",2};
    instr["movu"]={"01001",2};
    instr["movh"]={"01001",2};
    instr["lsl"]={"01010",3};
    instr["lsr"]={"01011",3};
    instr["asr"]={"01100",3};
    instr["nop"]={"01101",0};
    instr["ld"]={"01110",3};
    instr["st"]={"01111",3};
    instr["beq"]={"10000",1};
    instr["bgt"]={"10001",1};
    instr["b"]={"10010",1};
    instr["call"]={"10011",1};
    instr["ret"]={"10100",0};
    instr["hlt"]={"11111",0};
}
void generateErrors(int line, string str){                            //Generates Error
    cerr<< str <<" at line: "<< line;
    exit(0);
}
string trim(string s,int line){                                       //Trims code and cleans spaces
    int spaces=0;
    for(int i=0;i<2;i++){
        while(s.back()=='\t' or s.back()==' ')
            s.pop_back();
        reverse(s.begin(),s.end());
    }
    string temp;
    int len=s.size();
    for(int i=0;i<len;){
        if(s[i]==':'){
            temp+=":";
            if(i==len-1 or s[i+1]!=' ')
                temp+=" ";
            i++;
            continue;
        }
        if(s[i]=='/')
            break;
        if(s[i]!=' ' and s[i]!='\t'){
            temp+=s[i];
            i++;
            continue;
        }
        temp+=" ";
        int j=i;
        while(s[i]==s[j] and j<len)
            j++;
        i=j;
    }
    while(temp.length()!=0 && (temp.back()=='\t' || temp.back()==' '))
        temp.pop_back();
    for(int i=0;i<temp.length();i++){
        if(temp[i]==' ')
            spaces++;
    }
    return temp;
}
string imm_to_Binary(int imm)                                         //Converts immediate to binary
{
    if (imm < -131072 || imm > 131071) 
    {
        cerr << "Error: Immediate value out of range (-131072 to 131071)\n";
        exit(0);
    }
    bitset<16> binary(imm);
    return binary.to_string();
}
vector<string> lexer(const string& line) {                            //Lexer to divide code into tokens/lexemes
    vector<string> tokens;
    stringstream ss(line);
    string token;
    while (ss >> token){
        tokens.push_back(token);
    }
    return tokens;
}
void processLabels(){                                                 //Stores labels in label map
    int address=0;
    for(const string &line : filtered){
        vector<string> tokens=lexer(line);
        if(tokens.empty())  
            continue;
        if(tokens[0].back()==':'){
            string label=tokens[0].substr(0,tokens[0].size()-1);
            labels[label]=address;
        }
        address+=4;
    }
}
void parser(){                                                        //Parses entire code and checks syntax
    for(int i=0;i<filtered.size();i++){
        vector<string> line=lexer(filtered[i]);
        if(line.empty())    continue; 
        if(line[0].back()==':'){
            parseTree[i].label=line[0].substr(0,line[0].size()-1);
            parseTree[i].labelPresent=true;
            if(line.size()==1){
                generateErrors(i+1,"Only label present");
            }
        }
        else{
            parseTree[i].labelPresent=false;
            parseTree[i].label=" ";
            if(instr.count(line[0])!=0){
                parseTree[i].instruction=line[0];
            }
            else{
                generateErrors(i+1,"Invalid instruction");
            }
        }
        for(int j=1;j<line.size();j++){
            if(j==1){
                if(parseTree[i].labelPresent){
                    if(instr.count(line[j])!=0)
                        parseTree[i].instruction=line[j];
                    else{
                        generateErrors(i+1,"Invalid instruction");
                    }
                    continue;
                }
                else{
                    parseTree[i].operand.push_back(line[j]);
                    continue;
                }
            }
            if((j-parseTree[i].labelPresent==2) and (parseTree[i].instruction=="ld" or parseTree[i].instruction=="st")){
                parseTree[i].operand.push_back(line[j].substr(line[j].size()-3,2));
                parseTree[i].operand.push_back(line[j].substr(0,line[j].size()-4));
            }
            else
                parseTree[i].operand.push_back(line[j]);
        }
        if(instr[parseTree[i].instruction].second!=parseTree[i].operand.size()){
            generateErrors(i+1,"Invalid no. of operands");
        }
    }
}
void secondPass(){                                                    //Second Pass that converts assembly code to machine code
    int pc=0;
    for(const auto &entry:parseTree){
        if(entry.instruction.empty())
            continue;
        string binaryInstr=instr[entry.instruction].first;
        int operandCount=instr[entry.instruction].second;
        string binaryOperands;
        if(operandCount>1){
            string checkImm=entry.operand[operandCount-1];
            if(!registers.count(checkImm) and !labels.count(checkImm))
                binaryInstr+="1";
            else
                binaryInstr+="0";
        }
        if(instr[entry.instruction].second>1){
            if(entry.instruction.back()=='u')
                binaryInstr+="01";
            else if(entry.instruction.back()=='h')
                binaryInstr+="10";
            else
                binaryInstr+="00";
        }
        if(operandCount==0){
            while(binaryOperands.size()<27)
                binaryOperands+="0";
        }
        if(entry.instruction=="cmp")
            binaryOperands+="0000";
        for(int i=0;i<operandCount;i++){
            string operand=entry.operand[i];
            if(i==1 and (entry.instruction=="not" or entry.instruction=="mov"))
                binaryOperands+="0000";
            if(registers.count(operand)){
                binaryOperands+=registers[operand];
            }
            else if(labels.count(operand)){
                int address=labels[operand];
                bitset<27> addrBits((address-pc)/4);
                binaryOperands+=addrBits.to_string();
            }
            else{
                int imm=stoi(operand);
                binaryOperands+=imm_to_Binary(imm);
            }
        }
        string finalBinary=binaryInstr+binaryOperands;
        while(finalBinary.size()<32)
            finalBinary+="0";
        machineCode.push_back(finalBinary);
        pc+=4;
    }
}
void firstPass(){                                                     //First Pass that stores labels and parses code
    processLabels();
    parser();
    secondPass();
}
void writeToFile(){                                                   //To text file                                  
    ofstream outfile("MachineCode.txt");
    if (!outfile) {
        cerr << "Error: Unable to create MachineCode.txt file!\n";
        exit(1);
    }
    for (const string &code : machineCode) {
        outfile << code << "\n";
    }
    outfile.close();
}
int main(){                                                           //main function
    ISA();                                                                      
    ifstream infile;
    string fileName;
    cout<<"Enter assembly file name (e.g., input.asm): ";
    cin>>fileName;
    infile.open(fileName);
    if(infile.fail()){
        cerr<<"Error: Unable to open file!\n";
        return 1;
    }
    string line;
    while(getline(infile,line)){
        line=trim(line,static_cast<int>(filtered.size()));     
        if(!line.empty())
            filtered.push_back(line);
    }
    firstPass();
    for(const string &code:machineCode){
        cout<<code<<'\n';
    }
    writeToFile();
    return 0;
}
