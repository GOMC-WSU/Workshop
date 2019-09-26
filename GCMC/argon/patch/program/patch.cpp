//c++ version of patching program
//Program is written to do binary mixtures.  Will need some clean up to handle single components.
#include<vector>
#include<fstream>
#include<string>
#include<ios>
#include<iomanip>
#include<iostream>
#include<cmath>
#include<ctime>
#include <stdexcept>
#include <map>
#include <cstdlib>
#include "stoid.h"
using std::cerr;
using std::cout;
using std::endl;
using std::string;
using std::vector;
using std::ifstream;
using std::ofstream;
using std::setw;
using std::setfill;
using std::setprecision;
using std::clock_t;
using std::clock;
using std::map;
double min(double, double);
double max(double, double); 
int main()
{
  //read histogram labels
  clock_t start_time = std::clock();
  string suffix;
  int nhist;
  int ncompin;
  ifstream fin;
  fin.open("input_hs.dat");
  fin >> ncompin;
  fin >> suffix;
  fin >> nhist;
  vector<int> histid;
  int temp;
  for (int i=0; i<nhist; ++i){  
    fin >>temp;
    histid.push_back(temp);
  }
  fin.close();
  
  // build filenames and read histograms

  double t[nhist];
  double beta[nhist]; //inverse temperature
  int ncomp[nhist];
  double mu[nhist][ncompin];
  double mu1;
  double mu2;
  double weight[nhist];
  double oldweight[nhist];
  double lx[nhist];
  double ly[nhist];
  double lz[nhist];
  int minp[nhist][ncompin];
  int maxp[nhist][ncompin];
  int maxp_overall[ncompin];
  vector<string> histname;
  double xbox;
  double ybox;
  double zbox;
  vector<vector<int> > n[ncompin];
  vector<vector<int> > n1;
  vector<vector<int> > n2;
  vector<vector<double> > e;
  vector<int> n1t;
  vector<int> n2t;
  vector<double> et;
  vector<int> nentry;
  int ntemp1;
  int  ntemp2;
  double etemp;
  double crap;
  string s;
  double a;
  double b;
  int ncompin_old;
  int nhist_old;
  bool oldrun;

  clock_t io_start_time = std::clock();

  //see if we already have weights to use as an initial guess
  ifstream fin2;
  fin2.open("weights.dat");
  if (fin2){
    oldrun = true;
    cout << "Reading weights from: weights.dat" << endl;
    cout << setfill('=')<<setw(60) << "=" <<setfill(' ')<<endl;

    int i = 0;
    string temp;
    fin2 >> ncompin_old;
    fin2 >> nhist_old;
    fin2 >> suffix;
    for (int i=0; i<nhist_old; ++i){
      fin2 >> histid[i] >> temp >> oldweight[i] >> t[i] >> mu[i][0] >> mu[i][1];
      cout << setw(4) << histid[i] << std::scientific<<setprecision(6) <<setw(14) <<oldweight[i]<< std::fixed <<setprecision(2) <<setw(8)<< t[i] << setw(10) << mu[i][0] <<setw(10)<< mu[i][1] <<endl;
    }
    fin2.clear();
    fin2.close();
    if (nhist > nhist_old){
      for (int i=nhist_old; i<nhist; ++i){
	oldweight[i] = 100000000.0;
      }
    }
      
  }
  else if (!fin2) {
    oldrun = false;
    for (int i=0; i<nhist; ++i){
      oldweight[i] = 100000000.0;
    }
  }
 cout << setfill('=')<<setw(60) << "=" <<setfill(' ')<<endl;


  cout << "Patching histograms" <<endl;
  cout << ncompin << " component system" << endl;
  cout << "Reading " << nhist <<" histograms" <<endl;
  cout << endl;
  // cout << setfill('=')<<setw(80) << "=" <<setfill(' ')<<endl;
  cout <<setw(8) << "Histogram" << setw(8) <<"Nentry" <<setw(8)<< "Temp" << setw(10) << "mu1" <<setw(10)<< "mu2" << setw(8) << "n1-min" <<setw(8) << "n1-max" << setw(8) << "n2-min" <<setw(8) << "n2-max"<<endl;
 cout << setfill('=')<<setw(80) << "=" <<setfill(' ')<<endl;
  cout <<std::fixed;
  for (int i=0; i<nhist; ++i){
    //build file names
    string filein;
    for (int j=0;j<ncompin; ++j){
      minp[i][j] = 1e5;
      maxp[i][j] = -1e5;
    }
    filein = "his"+itos(histid[i])+suffix+".dat";
    histname.push_back(filein);
    fin.open(filein.c_str());
    //read header information
    if (ncompin == 2){
      fin >> t[i] >> ncomp[i] >> mu[i][0] >> mu[i][1] >> lx[i] >> ly[i] >> lz[i];
       // mu[i][0] used because C++ is backwards of fortran.  C++ = row-major order
    }
    else if (ncompin == 1){
      fin >> t[i] >> ncomp[i] >> mu[0][i] >> lx[i] >> ly[i] >> lz[i];
    }
   
    beta[i] = 1.0/t[i];

    //error checking
      if(ncompin != ncomp[i]){
        cerr << "Mismatch between number of components in input_hs.dat and histogram file "<< histname[i] << endl;
	cerr << "Components in input_hs.dat = " << ncompin << endl;
	cerr << "Components in histogram = " <<ncomp[i] <<endl;
	exit(1);
     }
      // set initial box size.  Check all other histograms to make sure they were run for the same system size.
    if (i==0){
      xbox = lx[i];
      ybox = ly[i];
      zbox = lz[i];
    }
    else if (i!=0) {
      if (xbox != lx[i] || ybox !=ly[i] || zbox !=lz[i]){
	cerr << "System size in histogram " << filein << " is inconsistent with other files" <<endl;
	exit(1);
      }
    }
      int j=0;
      while(fin){
	if (ncompin == 2){
	  fin >> ntemp1 >> ntemp2 >> etemp;
	
	  minp[i][0] = min(minp[i][0],ntemp1);
	  minp[i][1] = min(minp[i][1],ntemp2);
	  maxp[i][0] = max(maxp[i][0],ntemp1);
	  maxp[i][1] = max(maxp[i][1],ntemp2);

	  maxp_overall[0]= max(maxp[i][0],maxp_overall[0]);
	  maxp_overall[1]= max(maxp[i][1],maxp_overall[1]);

	  n1t.push_back(ntemp1);
	  n2t.push_back(ntemp2);
	  et.push_back(etemp);
	
	 }
	else{
	  fin >> ntemp1 >> etemp;

	  minp[i][0] = min(minp[i][0],ntemp1);
	  maxp[i][0] = max(maxp[i][0],ntemp1);

	  maxp_overall[0]= max(maxp[i][0],maxp_overall[0]);

	  n1t.push_back(ntemp1);
	  et.push_back(etemp);
	  //cerr << "haven't coded this yet" <<endl;
	  }
	++j;
      }
      //move data from temporary variables into vectors.  First index is component,
      // second index is file name, third is the data label
      if (ncompin == 1){
	n[0].push_back(n1t);
	e.push_back(et);
	nentry.push_back(n[0][i].size()-1);
	cout << setprecision(2) <<setw(8) << histname[i] << setw(8) <<nentry[i] <<setw(8)<< t[i] << setw(10) << mu[i][0] <<setw(8) << minp[i][0] <<setw(8)<< maxp[i][0] <<setw(8)<<endl;
      //clear temporary arrays, otherwise "bad things" happen
	n1t.clear();
	n2t.clear();
	et.clear();
      }
      else if (ncompin ==2){
	n[0].push_back(n1t);
	n[1].push_back(n2t);
	e.push_back(et);
	nentry.push_back(n[0][i].size()-1);
	cout << setprecision(2) <<setw(8) << histname[i] << setw(8) <<nentry[i] <<setw(8)<< t[i] << setw(10) << mu[i][0] <<setw(10)<< mu[i][1] <<setw(8) << minp[i][0] <<setw(8)<< maxp[i][0] <<setw(8)<< minp[i][1]<<setw(8) << maxp[i][1]<<endl;
      //clear temporary arrays, otherwise "bad things" happen
	n1t.clear();
	n2t.clear();
	et.clear();
      }
      // cout << "number of entries = " << nentry[i] <<endl;
     
      fin.clear();
      fin.close();
  }
  cout << "Histogram data read successfully" <<endl
       << "Read took " << ((clock() - io_start_time)/(double)CLOCKS_PER_SEC)
       << " (s)" <<endl; 

  

  int iter = 0;
  double prob;
  double tmp1;
  double val;
  double kCache = 0.0;
  oldweight[0] = weight[0] = 1.0;
  

  clock_t conv_step_start_time;
  
  cout << endl << "Starting pairwise convergence." << endl << endl;
  for (int l=2; l<3; ++l)
  {
     for (int k1=0; k1<=nhist-l; ++k1)
     {
	int kn = k1 + (l-1);
	conv_step_start_time=clock();
	cout << "Converging hist.: ( " <<  k1 << "-" << kn << " ) ";
	double maxd = 500;
	double tol = 5e-5;
	double y = 0.0;
	double ylog = -1e9;
      
	kCache = oldweight[k1];

	//normalize old weights.
	for (int h = k1; h<=kn; ++h)
        {
	   oldweight[h] /= kCache;
	}

	while (maxd > tol && iter < 1e4)
	{
	   ++iter;
	   maxd = 0.0;
	   for (int kH=k1; kH<=kn; ++kH)
	   {
	      weight[kH] = 0.0;
	      for (int iH=k1; iH <= kn; ++iH)
	      {
		 for (int i=0; i<nentry[iH]; ++i)
		 {
		    y=0.0;
		    ylog = -1e9;
		    for(int jH=k1; jH<= kn; ++jH)
		    {
		       prob = -(beta[jH]-beta[kH])*e[iH][i];
		       for (int icomp=0; icomp < ncompin; ++icomp)
		       {
			  prob += (beta[jH]*mu[jH][icomp]-
				   beta[kH]*mu[kH][icomp])*
			     n[icomp][iH][i];
		       }
		       // The following is a code rearrangement to 
		       // avoid overflow problems
		       // Replace y with log(y)
		       // Define log_expsum(y,z) = log(exp(y)+exp(z)
		       // Evaluate log_expsum(y,z) = max(y,z) + 
		       //            log(1+exp(-abs(y-z)))
		       tmp1 = prob +
			  log(nentry[jH]/oldweight[jH]);
		       ylog = max(ylog,tmp1) +
			  log(1.0+exp(-fabs(ylog-tmp1)));
		       //cout << tmp1 << endl;
		    }
		    weight[kH] = weight[kH]+exp(-ylog);
		 }
	      }
	      val = fabs(weight[kH]/oldweight[kH]-1);
	      if (val > maxd) maxd = val;
	   }
	   cout << "Converge " << setprecision(10) << maxd <<endl;
	   //normalize weights

	   for (int h = k1+1; h<=kn; ++h)
	   {
	      weight[h]/=weight[k1];
	      oldweight[h] = weight[h];
	   }
	   weight[k1] = oldweight[k1] = 1.0;
	}
	for (int h = k1; h <= kn; ++h)
	{
	   weight[h] *= kCache;
	   oldweight[h] = weight[h];
	}
     
	ofstream fout;
	fout.open("weights.dat");
	fout << ncompin <<endl << nhist <<endl <<suffix << endl;
	for (int ifile=0; ifile <nhist; ++ifile)
	{
	   fout << setw(4) << histid[ifile] << setw(10)
		<< nentry[ifile] << setw(20) << std::scientific 
		<< setprecision(8) << weight[ifile] << setw(10)
		<< std::fixed << setprecision(2) << t[ifile] 
		<< setw(10) << mu[ifile][0] << setw(10) 
		<< mu[ifile][1]<<endl;
	}
	fout << "Total iteractions = " << iter << endl
	     << "Convergence = " << setprecision(10) 
	     << maxd << endl << "Run time "
	     << ((clock() - start_time)/(double)CLOCKS_PER_SEC) 
	  << " (s)" <<endl;
	fout.close();
	cout << ((clock() -
	       conv_step_start_time)/(double)CLOCKS_PER_SEC)
	     << " (s)" <<endl;
     }
  }
  cout << endl << "Finished set convergence!"
       << endl << endl;


   //Simultaenously converge up to kfile
   for (int kfile=nhist-1; kfile<nhist; ++kfile)
   {
      double maxd = 500;
      double tol = 5e-5;
      double y = 0.0;
      double ylog = -1e9;
      
      while (maxd > tol && iter < 1e4)
      {
	 ++iter;
	 maxd = 0.0;
	 for (int kH=0; kH<=kfile; ++kH)
	 {
	    weight[kH] = 0.0;
	    
	    for (int iH=0; iH <= kfile; ++iH)
	    {
	       for (int i=0; i<nentry[iH]; ++i)
	       {
		  y=0.0;
		  ylog = -1e9;
		  for(int jH=0; jH <= kfile; ++jH)
		  {
		     prob = -(beta[jH]-beta[kH])*e[iH][i];
		     for (int icomp=0; icomp < ncompin; ++icomp)
		     {
			prob += (beta[jH]*mu[jH][icomp]-
				 beta[kH]*mu[kH][icomp])*
			   n[icomp][iH][i];
		     }
		     // The following is a code rearrangement to
		     // avoid overflow problems
		     // Replace y with log(y)
		     // Define log_expsum(y,z) = log(exp(y)+exp(z)
		     // Evaluate log_expsum(y,z) = max(y,z) +
		     // log(1+exp(-abs(y-z)))
		     tmp1 = prob + log(nentry[jH]/oldweight[jH]);
		     ylog = max(ylog,tmp1) +
			log(1.0+exp(-fabs(ylog-tmp1)));
		     //cout << tmp1 << endl;
		  }
		  weight[kH] = weight[kH]+exp(-ylog);
	       }
	       
	    }
	    val = fabs(weight[kH]/oldweight[kH]-1);
	    if (val > maxd) maxd = val;
	 }
	 for (int h=1; h<=kfile; ++h)
	 {
	    weight[h] = weight[h]/weight[0];
	    oldweight[h] = weight[h];
	    //      cout << weight[i] << endl;                         
	 }
	 weight[0] = oldweight[0] = 1.0;	 
	 //cout << "Converge 0-" << kfile << ": " 
	 //     << setprecision(10) << maxd <<endl;
	 ofstream fout;
	fout.open("weights.dat");
	fout << ncompin <<endl << nhist <<endl <<suffix << endl;
	for (int ifile=0; ifile <nhist; ++ifile)
	{
	   fout << setw(4) << histid[ifile] << setw(10)
		<< nentry[ifile] << setw(20) << std::scientific 
		<< setprecision(8) << weight[ifile] << setw(10)
		<< std::fixed << setprecision(2) << t[ifile] 
		<< setw(10) << mu[ifile][0] << setw(10) 
		<< mu[ifile][1]<<endl;
	}
	fout << "Total iteractions = " << iter << endl
	     << "Convergence = " << setprecision(10) 
	     << maxd << endl << "Run time "
	     << ((clock() - start_time)/(double)CLOCKS_PER_SEC) 
	  << " (s)" <<endl;
	fout.close();
	cout << ((clock() -
	       conv_step_start_time)/(double)CLOCKS_PER_SEC)
	     << " (s)" <<endl;
      }
      //normalize weights'
      
      
      ofstream fout;
      fout.open("weights.dat");
      fout << ncompin <<endl << nhist <<endl <<suffix << endl;
      for (int ifile=0; ifile <nhist; ++ifile)
      {
	 fout << setw(4) << histid[ifile] << setw(10)
	      << nentry[ifile] << setw(20) << std::scientific
	      << setprecision(8) << weight[ifile] << setw(10)
	      << std::fixed << setprecision(2) << t[ifile]
	      << setw(10) << mu[ifile][0]
	      << setw(10) << mu[ifile][1]<<endl;
      }
      fout << "Total iteractions = " << iter <<endl
	   << "Convergence = " <<setprecision(10)<< maxd << endl
	   << "Run time "
	   << ((clock() - start_time)/(double)CLOCKS_PER_SEC)
	   << " (s)" <<endl;
      fout.close();
   }

}

double min(double x, double y){
  if (x < y){
    y=x;
  }
  return y;
}

double max(double x, double y){
  if (x > y){
    y=x;
  }
  return y;
}

