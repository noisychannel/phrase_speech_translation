/*

fstprintpath-main.cpp

split out the main function call for fstprintpath

author: chris taylor

TODO: better support for command line arguments.

*/

#include <string>
#include "fstprintpaths.hpp"

using namespace std;
using namespace openfsttools;

int main(int argc, char** argv)
{
    if(argc < 2) { fprintf(stderr, "requires an openfst fst input file to print!\n"); }

    string* seqToSkip = NULL;

    if(argc == 4) {
       seqToSkip = new string( argv[3] );
    }
    else {
        seqToSkip = new string( "<EPS>" );
    }

    string symtabFilename(argv[1]);
    SymbolTable* st = SymbolTable::ReadText(symtabFilename);

    string fstToPrintFilename(argv[2]);
    StdVectorFst* finalFst = StdVectorFst::Read(fstToPrintFilename);

    fstprintpaths::printAllStrings( (*finalFst), (*st), (*seqToSkip) );

    delete st;
    delete finalFst;
    if(seqToSkip != NULL) { delete seqToSkip; }
}

