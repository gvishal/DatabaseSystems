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
    #define debug(args...) ; // Just strip off all debug tokens
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

int main(int argc, char *argv[]){
    ll size = (ll)atoi(argv[1])*1000*1000;
    ll oneRecord = 18;

    ll totalRecords = size/oneRecord;
    cout << size << space << totalRecords << endl;
    ofstream out(argv[1]);
    // static const string alphanum = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
    static const char alphanum[] = "0123456789"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    string line;
    stringstream ss;
    REP(k, 1, totalRecords){
        line.clear();
        REP(j, 1, 3){
            ss.str("");
            REP(i, 1, 5){
                ss << alphanum[rand() % (sizeof(alphanum) - 1)];
                // line.append(alphanum[rand() % (alphanum.length()-1)]);
            }
            line.append(ss.str());
            line.append(" ");
        }
        // cout<<line<<endl;
        // return 1;
        out << line << endl;
    }
    out.close();
    return 0;
}