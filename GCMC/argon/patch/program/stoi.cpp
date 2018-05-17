#include <sstream>
#include <string>
int stoi(std::string s){

  std::stringstream temp(s);
  int i;
  temp >> i;
  return i;
}

double stod(std::string s){
  
  std::stringstream temp(s);
  double x;
    temp >> x;
  return x;
}

std::string itos(int i){
  std::stringstream temp;
  std::string s;
  temp << i;
  temp>>s;
      return s;
}
