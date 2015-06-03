/*

fstprintpath-main.cpp

split out the main function call for fstprintpath

author: chris taylor

TODO: better support for command line arguments.

author: Gaurav Kumar 

Changed to print paths using a vector : Can take care of multiple paths in a DFS manner
Added cli options to print input output or both


*/

#include <string>
#include "fstprintpaths.hpp"

using namespace std;
using namespace openfsttools;

int main(int argc, char** argv)
{
    if(argc < 2) { fprintf(stderr, "requires an openfst fst input file to print!\n"); }

    string* seqToSkip = NULL;
    int mode = atoi( argv[3] );
    if(argc == 5) {
       seqToSkip = new string( argv[4] );
    }
    else {
        seqToSkip = new string( "<eps>" );
    }

    string symtabFilename(argv[1]);
    SymbolTable* st = SymbolTable::ReadText(symtabFilename);

    string fstToPrintFilename(argv[2]);
    StdVectorFst* finalFst = StdVectorFst::Read(fstToPrintFilename);

    fstprintpaths::printAllStrings( (*finalFst), (*st), (*seqToSkip), mode);

    delete st;
    delete finalFst;
    if(seqToSkip != NULL) { delete seqToSkip; }
}

