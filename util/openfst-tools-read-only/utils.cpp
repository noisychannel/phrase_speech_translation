/*

utils.cpp

contains reusable, and generically suited functions for reuse

author: chris taylor

*/
#include "utils.hpp"    

#include <iostream>
#include <sstream>

string vectorToString(vector<int>& v)
{
    if(v.size() == 0) { return "<>"; }

    string result = "<" + itos(v[0]);
    for(int i = 1; i < v.size(); i++) {
        result + "," + itos(v[i]);
    }

    return result + ">";
}

// convert int to string from Bjarne Stroustrup's FAQ
string itos(int i)
{
    stringstream s;
    s << i;
    return s.str();
}

