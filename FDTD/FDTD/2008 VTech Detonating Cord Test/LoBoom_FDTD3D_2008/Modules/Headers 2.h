/******************************************************************************
 *
 *  Headers.h
 *
 *  written by:     Sang Ik Cho
 *                  stc142@psu.edu 
 *  last modified:  7 / 22 / 2011
 *     
 *    This headear module contains all of the library headers, variable type 
 *  definition, and declaration of global variables, file input/output streams, 
 *  and function prototypes for LoBoomFDTD3D_SingleBldg program.  This header 
 *  must be included in the main function and every member modules for correct 
 *  compilation of the program.
 *    
 ******************************************************************************/

#include <iostream>
#include <fstream>
#include <math.h>
#include <omp.h>
#include <vector>
#include <string>

using namespace std;

// Definition of Custom Variable Types
struct GridPoint {
  bool InOrOut;
  float px;
  float py;
  float pz;
  float u;
  float v;
  float w;
};

struct Mic {
  int i,j,k;
};

typedef vector<vector<vector<GridPoint> > > Grid3D;
typedef vector<float> Array;

// Global Variables
extern string str_input_name;
extern float fs,rho,c0,z0,dx,CFL,dt,t_max,sigma_m,B,angle_elv,theta,angle_azm,phi;
extern int input_length_i,boom_length_i,D,n_max;
extern float bldg_dim_x,bldg_dim_y,bldg_dim_z,bldg_offset_x,bldg_offset_y,buffer_dim_x,buffer_dim_y,buffer_dim_z;
extern float boom_duration,x_intersect;
extern float dom_dim_x,dom_dim_y,dom_dim_z;
extern int i_intersect,I_MAX,J_MAX,K_MAX;
extern int bldg_dim_i,bldg_dim_j,bldg_dim_k,bldg_offset_i,bldg_offset_j;
extern int wall_loc_i1,wall_loc_i2,wall_loc_j1,wall_loc_j2,wall_loc_k1,wall_loc_k2;
extern int num_frame_yz,num_frame_xz,num_frame_xy,n_skip_yz,n_skip_xz,n_skip_xy;
extern float x_slice_yz,y_range_yz1,y_range_yz2,z_range_yz1,z_range_yz2;
extern float y_slice_xz,x_range_xz1,x_range_xz2,z_range_xz1,z_range_xz2;
extern float z_slice_xy,x_range_xy1,x_range_xy2,y_range_xy1,y_range_xy2;
extern int i_slice_yz,j_range_yz1,j_range_yz2,k_range_yz1,k_range_yz2;
extern int j_slice_xz,i_range_xz1,i_range_xz2,k_range_xz1,k_range_xz2;
extern int k_slice_xy,i_range_xy1,i_range_xy2,j_range_xy1,j_range_xy2;
extern int n_frame_surface,n_skip_surface,num_mics;
extern Mic* mics;

// File I/O stream
extern ofstream p_3D_init, p_2DYZ, p_2DXZ, p_2DXY, p_mic, p_surface;

// Function Prototypes
extern void ReadParameters();
extern void InitializeDataFiles();
extern void InitializeMatrix(Grid3D &, Array &, Array &);
extern void EulerPML3D(Grid3D &, Grid3D &, Array &);
extern void VisualizeMatrix(Grid3D &, int);
