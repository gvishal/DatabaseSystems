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
int noRecords;

map<string, int> colSize;
map<string, int> colName;
vector<int> sortOrder;

vector<int> recordsPresentBlock(1000, 0); //no of records present in block.
// Track last record read into memory
vector<int> currentRecordReadBlock(1000, 0); //current record on in block.

//Actual block vector to be used for loading blocks. Its size is limited by file size.
vector<vector<string> >  block; 
vii blockStatus; //Keep starting and ending status of each block
vi blockStatusCurrent; //Keep current position in miniblock
bool blockOver[1000] = {0};

ofstream finalOutput;

int read_metadata(){
    string line;
    
    ifstream meta("metadata.txt");

    if(!meta){
        return 1;
    }
    // Read metadata
    string col;
    int size, colNo = 0;

    while(getline(meta, line)){
        string delimit = ",";
        col = line.substr(0, line.find(delimit));
        size = atoi(line.substr(line.find(delimit)+1).c_str());
        colSize[col] = size;
        colName[col] = colNo++;
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

    if(read_metadata()){
        cout<<"Unable to read metadata\n";
    }

    REP(i, 5, argc-1){
        sortOrder.pb(colName[argv[i]]);  
    }

    string line;
    ifstream IN(argv[1]);

    getline(IN, line);
    cout<<line<<endl;
    recordLength = (int)line.length();
    noRecords = 1;

    while(getline(IN, line)){
        noRecords++;
    }

    cout << "Record length and no of records: " << recordLength << space << noRecords << endl;

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

    cout << "Blocks separated into files" << endl;
    // sorted the indivisual blocks.
    REP(i, 1, noBlocks){
        sortBlock(i);
    }

    cout << "indivisual block sorted and written into file" << endl; 

    block.resize(recordsBlock+5);
    blockStatus.resize(recordsBlock+5);
    blockStatusCurrent.resize(recordsBlock+5);
    int recordsMiniBlock = recordsBlock / (noBlocks + 1); // 1 additional for output
    cout << "records miniblocks: " << recordsMiniBlock << endl;
    REP(i, 0, noBlocks){
        blockStatus[i].first = i*recordsMiniBlock;
        blockStatus[i].second = (i+1)*recordsMiniBlock - 1;
        blockStatusCurrent[i] = i*recordsMiniBlock;
    }
    // Merge the indivisual blocks
    finalOutput.open(argv[2]);

    mergeBlocks(noBlocks);

    finalOutput.close();

    return 0;
}

priority_queue<pair<vector<string>, int>, vector<pair<vector<string>, int> >, greater<pair<vector<string>, int> > > ascending;
priority_queue<pair<vector<string>,int>,vector<pair<vector<string>,int> > > descending;
// priority_queue<pair<vector<string>,int>,vector<pair<vector<string>,int> > > *pq[2];

int loadBlock(int n){
    // Load ith block from next record onwards
    ifstream in(to_string(n));
    int currentRecordToRead = currentRecordReadBlock[n] + 1;
    if(currentRecordToRead > recordsPresentBlock[n]){
        cout<<"Block over\n";
        blockOver[n] = true;
        return 1;
    }
    debug("in.tellg() Before seekg", in.tellg());
    in.seekg((currentRecordToRead-1) * (recordLength+1));
    debug("in.tellg() After seekg", in.tellg());
    string line;
    int start = blockStatus[n].first;
    int end = blockStatus[n].second;
    blockStatus[n].second = start-1;
    debug("miniblock Read: start, end, currentRecordToRead, currentRecordReadBlock[n], blockStatusCurrent[n]",
        start, end, currentRecordToRead, currentRecordReadBlock[n], blockStatusCurrent[n]);

    REP(i, start, end){
        if(currentRecordReadBlock[n] == recordsPresentBlock[n]){
            // blockOver[n] = true;
            break;
        }
        getline(in, line);
        if(i < start + 3)debug("first few lines read from block: ", line)
        // if(!getline(in, line)){
        //     blockOver[n] = true;
        //     break;
        // }
        vector<string> tokens;
        string token;
        istringstream iss(line);
        while(iss >> token)tokens.pb(token);
        block[i] = tokens;
        // for(auto k: block[i])
        //     cout<<k<<space;
        currentRecordReadBlock[n]++;
        blockStatus[n].second++;
    }
    blockStatusCurrent[n] = start;
    debug("miniblock Read ended: start, end, currentRecordToRead, currentRecordReadBlock[n], blockStatusCurrent[n]",
        blockStatus[n].first, blockStatus[n].second, currentRecordToRead, currentRecordReadBlock[n], blockStatusCurrent[n]);
    return 0;
}


void storeBlock(){
    // Write 0th miniblock into finalOutput
    int start = blockStatus[0].first;
    int end = blockStatus[0].second;

    if(blockStatusCurrent[0] < end)
        end = blockStatusCurrent[0];

    debug("Storing block blockStatus[0].first, blockStatus[0].second, start, end, blockStatusCurrent[0]: ", blockStatus[0].first, blockStatus[0].second, start, end, blockStatusCurrent[0])
    REP(i, start, end){

        string line;
        for(auto j:block[i]){
            line.append(j);
            if(j != block[i][block[i].size()-1])
                line.append(" ");
        }
        // cout<<line<<endl;
        if(i == start)debug("First output record: ", line);
        if(i == end)debug("Last output record: ", line);
        finalOutput << line << endl;
    }
    // Block is clear, so reset it.
    blockStatusCurrent[0] = start;
    debug("Storing block Done: blockStatus[0].first, blockStatus[0].second, start, end, blockStatusCurrent[0]: ", blockStatus[0].first, blockStatus[0].second, start, end, blockStatusCurrent[0])

}

void loadPQ(int noBlocks){
    if(order == 0){
        auto *pq = &ascending;
        REP(i, 1, noBlocks){
            (*pq).push({block[blockStatusCurrent[i]++], i});
            // cout<<i<<"push :"<<(*pq).empty()<<endl;
        }
    } else {
        auto *pq = &descending;
        REP(i, 1, noBlocks){
            (*pq).push({block[blockStatusCurrent[i]++], i});
        }
    }
    
    return;
}

void printTrace(int);

void extractRecord(int noBlocks){
    if(order == 0){
        auto *pq = &ascending;
        // Check if outBlock is full or not
        
        REP(i, 1, noRecords){
            if(blockStatusCurrent[0] > blockStatus[0].second){
                cout << "Storing output block into file at record: " << i << endl;
                storeBlock();
            }

            // cout << i << "Into if"<< (*pq).empty() << endl;
            if(!(*pq).empty()){
                int outBlockPos = blockStatusCurrent[0]++;
                // Extract from queue
                // cout<<i<<"Here"<<endl;
                pair<vector<string>, int> p = (*pq).top();
                block[outBlockPos] = p.first;
                (*pq).pop();
                debug("Top of priority_queue: ", p.first[0], p.first[1], p.first[2])
                // Load a record into queue from p.second miniblock
                debug("Current popped block info: p.second, blockOver[p.second], blockStatusCurrent[p.second], \
                    blockStatus[p.second].second", p.second, blockOver[p.second], blockStatusCurrent[p.second],
                    blockStatus[p.second].second)
                if(!blockOver[p.second]){
                    // Check if miniblock is not over, if over load it from file
                    if(blockStatusCurrent[p.second] > blockStatus[p.second].second){
                        debug("Load block: p.second", p.second)
                        if(loadBlock(p.second)){
                            // Block over, move on!
                            continue;
                        }
                    }
                    debug("Push element: p.second, blockStatusCurrent[p.second], block[blockStatusCurrent[p.second]]",
                        p.second, blockStatusCurrent[p.second], block[blockStatusCurrent[p.second]][0], 
                        block[blockStatusCurrent[p.second]][1], block[blockStatusCurrent[p.second]][2] )
                    (*pq).push({block[blockStatusCurrent[p.second]++], p.second});
                } else {
                    debug("Block over: p.second, i, noBlocks", p.second, i, noBlocks)
                }
            } else {
                debug("Record: i, noRecords ", i, noRecords);
                debug("Pq empty, shouldn't have happened");
                storeBlock();
                debug("Trace of blocks: ");
                printTrace(noBlocks);
                exit(1);
            }
        }
        
        debug("Record: i, noRecords ", noRecords);
        debug("Pq empty, ");
        storeBlock();
        debug("Trace of blocks: ");
        printTrace(noBlocks);
    } else {
        auto *pq = &descending;
    }
}

void mergeBlocks(int noBlocks){

    REP(i, 1, noBlocks){
        loadBlock(i);
    }

    loadPQ(noBlocks);
    // cout<<ascending.empty()<<space<<descending.empty()<<endl;
    extractRecord(noBlocks);

    return;
}

void printTrace(int noBlocks){
    REP(i, 0, noBlocks){
        debug("Block ", i)
        debug("recordsPresentBlock: ", recordsPresentBlock[i])
        debug("currentRecordReadBlock: ", currentRecordReadBlock[i])
        debug("blockStatus: ", blockStatus[i].first, blockStatus[i].second)
        debug("blockStatusCurrent: ", blockStatusCurrent[i])
        debug("blockOver: ", blockOver[i])
    }
    debug("Main Block data: ");
    for(auto i:block){
        for(auto j:i){
            cout<<j<<space;
        }
        cout<<endl;
    }
    return;
}
