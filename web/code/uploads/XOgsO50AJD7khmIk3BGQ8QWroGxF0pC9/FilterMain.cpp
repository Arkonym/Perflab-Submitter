#include <stdio.h>
#include "cs1300bmp.h"
#include <iostream>
#include <stdint.h>
#include <fstream>
#include "Filter.h"

using namespace std;

#include "rtdsc.h"

//
// Forward declare the functions
//
Filter * readFilter(string filename);
double applyFilter(Filter *filter, cs1300bmp *input, cs1300bmp *output);

	int
main(int argc, char **argv)
{

	if ( argc < 2) {
		fprintf(stderr,"Usage: %s filter inputfile1 inputfile2 .... \n", argv[0]);
	}

	//
	// Convert to C++ strings to simplify manipulation
	//
	string filtername = argv[1];

	//
	// remove any ".filter" in the filtername
	//
	string filterOutputName = filtername;
	string::size_type loc = filterOutputName.find(".filter");
	if (loc != string::npos) {
		//
		// Remove the ".filter" name, which should occur on all the provided filters
		//
		filterOutputName = filtername.substr(0, loc);
	}

	Filter *filter = readFilter(filtername);

	double sum = 0.0;
	int samples = 0;

	for (int inNum = 2; inNum < argc; inNum++) {
		string inputFilename = argv[inNum];
		string outputFilename = "filtered-" + filterOutputName + "-" + inputFilename;
		struct cs1300bmp *input = new struct cs1300bmp;
		struct cs1300bmp *output = new struct cs1300bmp;
		int ok = cs1300bmp_readfile( (char *) inputFilename.c_str(), input);

		if ( ok ) {
			double sample = applyFilter(filter, input, output);
			sum += sample;
			samples++;
			cs1300bmp_writefile((char *) outputFilename.c_str(), output);
		}
		delete input;
		delete output;
	}
	fprintf(stdout, "Average cycles per sample is %f\n", sum / samples);

}

	struct Filter *
readFilter(string filename)
{
	ifstream input(filename.c_str());

	if ( ! input.bad() ) {
		int size = 0;
		input >> size;
		Filter *filter = new Filter(size);
		int div;
		input >> div;
		filter -> setDivisor(div);
		for (int i=0; i < size; i++) {
			for (int j=0; j < size; j++) {
				int value;
				input >> value;
				filter -> set(i,j,value);
			}
		}
		return filter;
	}
}

#if defined(__arm__)
static inline unsigned int get_cyclecount (void)
{
	unsigned int value;
	// Read CCNT Register
	asm volatile ("MRC p15, 0, %0, c9, c13, 0\t\n": "=r"(value)); 
	return value;
}

static inline void init_perfcounters (int32_t do_reset, int32_t enable_divider)
{
	// in general enable all counters (including cycle counter)
	int32_t value = 1;

	// peform reset: 
	if (do_reset)
	{
		value |= 2;     // reset all counters to zero.
		value |= 4;     // reset cycle counter to zero.
	}

	if (enable_divider)
		value |= 8;     // enable "by 64" divider for CCNT.

	value |= 16;

	// program the performance-counter control-register:
	asm volatile ("MCR p15, 0, %0, c9, c12, 0\t\n" :: "r"(value)); 

	// enable all counters: 
	asm volatile ("MCR p15, 0, %0, c9, c12, 1\t\n" :: "r"(0x8000000f)); 

	// clear overflows:
	asm volatile ("MCR p15, 0, %0, c9, c12, 3\t\n" :: "r"(0x8000000f));
}



#endif



	double
applyFilter(struct Filter *filter, cs1300bmp *input, cs1300bmp *output)
{
#if defined(__arm__)
	init_perfcounters (1, 1);
#endif

	long long cycStart, cycStop;
	double start,stop;
#if defined(__arm__)
	cycStart = get_cyclecount();
#else
	cycStart = rdtscll();
#endif
	output -> width = input -> width;
	output -> height = input -> height;
	int i,j,col,row,plane;
	int size = filter -> getSize();
	int i_width = input -> width;
	int i_height = input -> height;
	int getDiv= filter -> getDivisor();
  int getIJ[9];
  getIJ[0]= filter -> get(0, 0); 
	getIJ[1]= filter -> get(1, 0);
	getIJ[2]= filter -> get(2, 0);
	getIJ[3]= filter -> get(0, 1);
	getIJ[4]= filter -> get(1, 1);
	getIJ[5]= filter -> get(2, 1);
	getIJ[6]= filter -> get(0, 2);
	getIJ[7]= filter -> get(1, 2);
	getIJ[8]= filter -> get(2, 2);
  

	
		for(row = 1; row < i_height - 1 ; row = row + 1) {	
			for(col = 1; col < i_width - 1; col = col + 1) {    


				int t = 0;	
				int ot1 = 0;
				int ot2 = 0;
				int ot3 = 0;


			
        /////////////////////////////////////////////////
		
						ot1  = ot1 + (input -> color[0][row + 0 - 1][col + 0 - 1] * getIJ[0] );
						ot2  = ot2 + (input -> color[1][row + 0 - 1][col + 0 - 1] * getIJ[0] );
						ot3  = ot3 + (input -> color[2][row + 0 - 1][col + 0 - 1] * getIJ[0] );

						ot1  = ot1 + (input -> color[0][row + 1 - 1][col + 0 - 1] * getIJ[1] );
						ot2  = ot2 + (input -> color[1][row + 1 - 1][col + 0 - 1] * getIJ[1] );
						ot3  = ot3 + (input -> color[2][row + 1 - 1][col + 0 - 1] * getIJ[1] );

						ot1  = ot1 + (input -> color[0][row + 2 - 1][col + 0 - 1] * getIJ[2] );
						ot2  = ot2 + (input -> color[1][row + 2 - 1][col + 0 - 1] * getIJ[2] );
						ot3  = ot3 + (input -> color[2][row + 2 - 1][col + 0 - 1] * getIJ[2] );

					//
					  ot1  = ot1 + (input -> color[0][row + 0 - 1][col + 1 - 1] * getIJ[3] );
						ot2  = ot2 + (input -> color[1][row + 0 - 1][col + 1 - 1] * getIJ[3] );
						ot3  = ot3 + (input -> color[2][row + 0 - 1][col + 1 - 1] * getIJ[3] );

						ot1  = ot1 + (input -> color[0][row + 1 - 1][col + 1 - 1] * getIJ[4] );
						ot2  = ot2 + (input -> color[1][row + 1 - 1][col + 1 - 1] * getIJ[4] );
						ot3  = ot3 + (input -> color[2][row + 1 - 1][col + 1 - 1] * getIJ[4] );

						ot1  = ot1 + (input -> color[0][row + 2 - 1][col + 1 - 1] * getIJ[5] );
						ot2  = ot2 + (input -> color[1][row + 2 - 1][col + 1 - 1] * getIJ[5] );
						ot3  = ot3 + (input -> color[2][row + 2 - 1][col + 1 - 1] * getIJ[5] );
					//
						ot1  = ot1 + (input -> color[0][row + 0 - 1][col + 2 - 1] * getIJ[6] );
						ot2  = ot2 + (input -> color[1][row + 0 - 1][col + 2 - 1] * getIJ[6] );
						ot3  = ot3 + (input -> color[2][row + 0 - 1][col + 2 - 1] * getIJ[6] );

						ot1  = ot1 + (input -> color[0][row + 1 - 1][col + 2 - 1] * getIJ[7] );
						ot2  = ot2 + (input -> color[1][row + 1 - 1][col + 2 - 1] * getIJ[7] );
						ot3  = ot3 + (input -> color[2][row + 1 - 1][col + 2 - 1] * getIJ[7] );

						ot1  = ot1 + (input -> color[0][row + 2 - 1][col + 2 - 1] * getIJ[8] );
						ot2  = ot2 + (input -> color[1][row + 2 - 1][col + 2 - 1] * getIJ[8] );
						ot3  = ot3 + (input -> color[2][row + 2 - 1][col + 2 - 1] * getIJ[8] );
					//
					

        /////////////////////////////////////////////////
				
				ot1 = ot1/getDiv;	
				ot2 = ot2/getDiv;
				ot3 = ot3/getDiv;
				

				if ( ot1  < 0 ) {
					output -> color[0][row][col] = 0;
				}
				else if ( ot1  > 255 ) { 
					output -> color[0][row][col] = 255;
				}
				else
				{
					output -> color[0][row][col]=ot1;
				}
				if ( ot2  < 0 ) {
					output -> color[1][row][col] = 0;
				}
				else if ( ot2  > 255 ) { 
					output -> color[1][row][col] = 255;
				}
				else
				{
					output -> color[1][row][col]=ot2;
				}
				if ( ot3  < 0 ) {
					output -> color[2][row][col] = 0;
				}
				else if ( ot3  > 255 ) { 
					output -> color[2][row][col] = 255;
				}
				else
				{
					output -> color[2][row][col]=ot3;
				}
			}
		}
	
#if defined(__arm__)
	cycStop = get_cyclecount();
#else
	cycStop = rdtscll();
#endif

	double diff = cycStop-cycStart;
#if defined(__arm__)
	diff = diff * 64;
#endif
	double diffPerPixel = diff / (output -> width * output -> height);
	fprintf(stderr, "Took %f cycles to process, or %f cycles per pixel\n",
			diff, diff / (output -> width * output -> height));
	return diffPerPixel;
}
