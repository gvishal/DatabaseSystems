#include<bits/stdc++.h>
using namespace std;
//custom
#define endl ('\n')
#define space (" ")
#define __ ios_base::sync_with_stdio(false);cin.tie(0);
// Useful constants
#define INF (int)1e9
#define EPS (double)(1e-9)
#define PI (double)(3.141592653589793)
//utils
#define SET(a,b) (memset(a,b,sizeof(a)))
//for vectors
#define pb push_back
#define mp make_pair
typedef vector<int> vi; 
typedef pair<int,int> ii;
typedef vector<ii> vii;
//data types
typedef long long ll;
//loops
#define REP(i,a,b) \
    for(int i = int(a);i <= int(b);i++)
#define TRvi(c,it) \
    for(vi::iterator it=(c).begin();it!=(c).end();it++)
#define MEMSET_INF 127 //2bill
#define MEMSET_HALF_INF 63 //1bill

#ifdef DEBUG
    #define debug(args...) {dbg,args; cerr<<endl;}
    #define _
    #define OUT(A,a,b) for(int zi = a;zi <= int(b); zi++)cout<<A[zi]<<space;cout<<endl;
#else
    #define debug(args...)  // Just strip off all debug tokens
    #define _ ios_base::sync_with_stdio(false);cin.tie(0);
    #define OUT(A,a,b)
#endif 
struct debugger
{
    template<typename T> debugger& operator , (const T& v)
    {    
        cerr<<v<<" ";    
        return *this;    
    }
} dbg;

int order = 0;// 0 for asc
int recordLength;

map<string, int> colSize;
vector<int> sortOrder;

vector<int> recordsPresentBlock(200000, 0); //no of records present in block.
// Track last record read into memory
vector<int> currentRecordBlock(200000, 0); //current record on in block.

//Actual block vector to be used for loading blocks. Its size is limited by file size.
vector<vector<string> >  block; 
vii blockStatus; //Keep starting and ending status of each block
vi blockStatusCurrent; //Keep current position in miniblock
bool blockOver[200000] = {0};

int read_metadata(){
    string line;
    
    ifstream meta("metadata.txt");

    if(!meta){
        return 1;
    }
    // Read metadata
    string col;
    int size;

    while(getline(meta, line)){
        string delimit = ",";
        col = line.substr(0, line.find(delimit));
        size = atoi(line.substr(line.find(delimit)+1).c_str());
        colSize[col] = size;
    }
    return 0;
}

bool compare(vector<string> A,vector<string> B){
    REP(i, 0, sortOrder.size()-1){
        if(order == 0){
            // ascending
            if(A[sortOrder[i]] < B[sortOrder[i]] )
                return true;
            else if(A[sortOrder[i]] > B[sortOrder[i]] )
                return false;
        }
        if(order == 1){
            // descending
            if(A[sortOrder[i]] > B[sortOrder[i]] )
                return true;
            if(A[sortOrder[i]] < B[sortOrder[i]] )
                return false;
        }
    }
    return false;
}

void sortBlock(int i){
    ifstream blockFile(to_string(i));
    string line;
    block.clear();
    while(getline(blockFile, line)){
        // Space separate columns
        vector<string> tokens;
        string token;
        istringstream iss(line);
        while(iss >> token)tokens.pb(token);
        block.pb(tokens);
    }
    sort(block.begin(), block.end(), compare);

    // Write back to file
    ofstream out(to_string(i));
    for(auto k:block){
        line.clear();
        for(auto j:k){
            line.append(j);
            if(j != k[k.size()-1])
                line.append(" ");
        }
        out << line << endl;
    }
    out.close();
    block.clear();
}

void mergeBlocks(int);

int main(int argc, char *argv[]){
    // ./sort input.txt output.txt 50 asc c0 c1
    if(argc < 6){
        cout<<"Not enough arguments\n";
        return -1;
    }
    
    int memoryToUse = atoi(argv[3]);// In MB
    // memoryToUse -= 10; //reserve some memory

    if(strcmp(argv[4], "asc") == 0){
        order = 0;
    } else if(strcmp(argv[4], "desc") == 0){
        order = 1;
    } else{
        cout<<"Invalid sort order\n";
        return -1;
    }

    REP(i, 5, argc-1){
        sortOrder.pb(argv[i][1]-'0');
    }

    if(read_metadata()){
        cout<<"Unable to read metadata\n";
    }

    string line;
    ifstream IN(argv[1]);

    getline(IN, line);
    recordLength = (int)line.length();
    int noRecords = 1;

    while(getline(IN, line)){
        noRecords++;
    }
    IN.clear();                 // clear fail and eof bits
    IN.seekg(0);

    ll totalData = (ll)recordLength * (ll)noRecords;

    int noBlocks = totalData / ((ll)memoryToUse*1024*1024) + (totalData%((ll)memoryToUse*1024*1024) ? 1 : 0);
    int recordsBlock = noRecords / noBlocks;

    cout << "Total blocks to use: " << noBlocks << endl;
    cout << "Records per block: " << recordsBlock << endl;

    // Separate blocks into separate files
    REP(i, 1, noBlocks){
        string blockFile = to_string(i);
        // cout<<blockFile<<endl;
        ofstream out(blockFile);
        REP(j, 1, recordsBlock){
            if(!getline(IN, line)){
                cout<<j<<"No more lines present...exiting.\n";
                break;
            }
            out << line << endl;
            recordsPresentBlock[i]++;
        }
        out.close();
    }

    // sorted the indivisual blocks.
    REP(i, 1, noBlocks){
        sortBlock(i);
    }

    block.resize(recordsBlock+5);
    blockStatus.resize(recordsBlock+5);
    blockStatusCurrent.resize(recordsBlock+5);
    int recordsMiniBlock = recordsBlock / (noBlocks + 1); // 1 additional for output
    REP(i, 0, noBlocks){
        blockStatus[i].first = i*recordsMiniBlock;
        blockStatus[i].second = (i+1)*recordsMiniBlock - 1;
        blockStatusCurrent[i] = i*recordsMiniBlock;
    }
    // Merge the indivisual blocks
    mergeBlocks(noBlocks);

    return 0;
}

priority_queue<pair<vector<string>, int>, vector<pair<vector<string>, int> >, greater<pair<vector<string>, int> > > ascending;
priority_queue<pair<vector<string>,int>,vector<pair<vector<string>,int> > > descending;

void loadBlock(int n){
    // Load ith block from next record onwards
    ifstream in(to_string(n));
    int currentRecord = currentRecordBlock[n] + 1;
    if(currentRecord > recordsPresentBlock[n]){
        cout<<"Block over\n";
        return;
    }
    in.seekg((currentRecord-1) * (recordLength+1));
    string line;
    int start = blockStatus[n].first;
    int end = blockStatus[n].second;
    blockStatus[n].second = start;
    REP(i, start, end){
        if(!getline(in, line)){
            blockOver[n] = true;
            break;
        }
        vector<string> tokens;
        string token;
        istringstream iss(line);
        while(iss >> token)tokens.pb(token);
        block[i] = tokens;
        currentRecordBlock[n]++;
        blockStatus[n].second++;
    }
}

void mergeBlocks(int noBlocks){
    return;
}