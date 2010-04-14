#include <iostream>
#include <fstream>
#include <string.h>

//środa, 14 kwiecień 2010
//haha znalazlem go w katalogu poczatki z c++ ;}} 

using namespace std;

class Ostring
{            
        char *tablica;     
     public: 
        Ostring();
        ~Ostring();
        void operator<<(char *);
        char * zwroc();     
};//Ostring
Ostring::Ostring()
{
        tablica=new char[0];                
}
Ostring::~Ostring()
{           
        tablica=NULL;
}
void Ostring::operator<<(char *znaki)
{       
        char *_buffor;                                      
        _buffor = new char[strlen(tablica)+1];
        strcpy(_buffor,tablica);
        delete tablica;
        tablica = new char[strlen(_buffor)+strlen(znaki)+1];
        strcpy(tablica,_buffor);
        strcat(tablica,znaki);
        delete _buffor;
}
char * Ostring::zwroc()
{
        return tablica;                    
}

class IO_plik
{
        fstream plik;
        char *nazwa_pliku;
        char *buffor;       //max ilosc plikow
        char *adresy[300];  // tablica wsk. do przechowywania adresow www, http
        int i_w_z;          // ilosc wczytanych znakow z pliku
        int i_linkow;       // ilosc zapisanych linkow
     public:
        IO_plik(char *);
        ~IO_plik();
        char * czytaj_buff();
        void info();                     // wypisanie inormacji o pliku
        friend void szukaj(IO_plik&);
     protected:
        void flagi_stanu(fstream &);     // sprawdzenie aktualnego stanu flag w srumieniu

};//IO_plik

IO_plik::IO_plik(char *_nazwa_pliku) : nazwa_pliku(_nazwa_pliku),i_linkow(0)
{             
        char _buffor[100000];
        Ostring tablica;
        plik.open(nazwa_pliku,ios::in);
        if(!plik)
        {       cout<<"Utworz "<<nazwa_pliku<<" w katalogu macierzystym";
        
        }
        while(!plik.eof())  //sprawdzenie czy EndOfFile i wcztywanie pliku
        {       plik.get(_buffor,sizeof(_buffor),EOF);
                tablica<<_buffor;           // wypelnianie tablicy
                plik.seekg(plik.tellg());   // pozycjonowanie wskaznika
        }
        buffor=tablica.zwroc(); // przekazanie adrsu tablicy do wsk. buffor
        i_w_z=strlen(buffor);   // ilosc wczytanych znakow
        plik.clear();           // zeruje wszystkie flagi bledu i tym samym ustawiam flage goodbit na 1
                                // mozna napisac to w ten sposob plik.clear(plik.rdstate() | ~ios::eofbit | ~ios::failbit);
        plik.close();
}

IO_plik::~IO_plik()
{
        plik.open("czytaj.txt",ios::out|ios::trunc|ios::binary);
        if(!plik)
                cout<<"\nBlad zapisu,heheheh !!!\n";
        for(int i=0;i<i_linkow;i++)
                plik<<adresy[i]<<endl;
        plik.close();
        delete buffor;
        if(i_linkow>0)
                delete[] adresy;
}
void IO_plik::flagi_stanu(fstream &_plik)
{
        cout<<"\ngoodbit "<<_plik.good()
            <<"\n\neofbit  "<<_plik.eof()
            <<"\nfailbit "<<_plik.fail()
            <<"\nbadbit  "<<_plik.bad()<<endl;
}
char * IO_plik::czytaj_buff()
{   
        return buffor;
}
void IO_plik::info()
{
        cout<<"\nPlik "<<nazwa_pliku<<"\nIlosc wczytanych znakow "<<i_w_z
            <<"\nIlosc wylapanych linkow "<<i_linkow<<endl;           
}
void szukaj(IO_plik &adres)
{
        int a=0,k=0,i_p;
        const char http[]="http:";
        char _buffor[400];          //max
        for(int i=0;i<adres.i_w_z;i++)
        {
                if(adres.buffor[i]==http[a])
                   if(adres.buffor[i+1]==http[a+1])
                      if(adres.buffor[i+2]==http[a+2])
                         if(adres.buffor[i+3]==http[a+3])
                            if(adres.buffor[i+4]==http[a+4])
                            {
                              i_p=i-1;  // nr znaku znajdujacego sie przed www lub http ten znak powinien konczyc link zazwyczaj zaczyna sie od ' " ' i konczy na ' " '
                              if(adres.buffor[i_p]=='>')adres.buffor[i_p]='<'; //jesli link poprzedza znak " >www.wara.pl</a>" to koncowy znak to < (zakladam taki pzrypadek)
                              for(;;i++ & a++)
                              {
                                      _buffor[a]=adres.buffor[i];
                                      if(adres.buffor[i_p]==adres.buffor[i+1])   //sprawdzam znak poprzedzajacy link z ostatnio wczytanym znakiem jesli sa takie same to brake
                                              break;
                                      if(a>398)     //zabezpieczenie przed wysypaniem prog
                                      {
                                              cout<<"\nZa dlugi link, zostanie uciety";
                                              break;
                                      }
                              }
                              if(adres.buffor[i_p]=='>')adres.buffor[i_p]='>';   // jesli nie beda mi potrzebne pierwotne dane to ta linia jest zbedna
                              _buffor[a+1]=NULL;                              // oznaczam koniec string'u ostatni moze byc krotszy od poprzedniego
                              adres.adresy[k]=new char[strlen(_buffor)+1]; // szkoda pamieci
                              strcpy(adres.adresy[k],_buffor);
                              k++;
                              a=0;
                            }
        }
        adres.i_linkow=k;            // okreslam ilosc zdobytych linkow
}
int main(int argc,char *argv[])
{    
        char nazwa[30];
        if(argc==1){
                cout<<"Podaj nazwe pliku : ";
                cin.getline(nazwa,sizeof(nazwa));
        }else
             strcpy(nazwa,argv[1]);     
        IO_plik plik(nazwa);
        szukaj(plik);
        plik.info();
        cout<<"\nZakonczone !"<<endl;        
        
        return 0;
}
