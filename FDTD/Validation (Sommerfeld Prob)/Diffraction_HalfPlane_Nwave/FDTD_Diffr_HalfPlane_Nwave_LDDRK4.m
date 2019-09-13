%% FDTD_Diffr_HalfPlane_Nwave_LDDRK4.m
%
%   written by Sang-Ik Terry Cho
%   last modified on 4 / 11 / 2012
%   
%     This program simulates a Sommerfeld-type problem of a plane wave
%   diffraction by a rigid half plane using a 2-D FDTD method.  A simple 
%   2nd-order centered-difference scheme in spatial domain and the 4-stage
%   LDDRK time integration method were applied to the linearized Euler 
%   equations coupling acoustic pressure and particle velocity.
%     The rigid half-plane lies on the (+)ve x-axis, starting from the 
%   "origin".  A perfect N-wave is taken as the input and is used to 
%   initialize the computational domain with an incident boom and its 
%   reflection according to its incoming angle.  
%     The user specifies a number of simulation parameters including the 
%   input boom, its incoming angle, sound speed, grid size, domain 
%   boundaries, and the starting and ending times.
%
%   *** NOTE: MATLAB easily runs out of memory for fine grids ***

clear all, close all;
bluered=[linspace(0,1,100) ones(1,100); linspace(0,1,100) linspace(1,0,100); ones(1,100) linspace(1,0,100)]';

fig1 = figure('Position',[0 500 550 500]);
fig2 = figure('Position',[550 500 550 500]);
fig3 = figure('Position',[1100 500 550 500]);


%% Parameters
% Receiver locations
X_rcvr = [20, 0, -20, 0, 20];
Y_rcvr = [0.01, 20, 0, -20, -0.01];

% Time parameters
CFL = 1.0;
rho0 = 1.21;
c0 = 343;
t_start = -0.2;
t_end = 0.8;

% Domain parameters
dx = 1;
X_MIN = -400;
X_MAX = 400;
Y_MIN = -400;
Y_MAX = 400;

% Incoming signature parameters
N_duration = 0.5;
N_amplitude = 1;
N_slope = N_duration/2/N_amplitude;
theta0_deg = 120;

% LDDRK Parameters
c_LDDRK4 = [1, 1/2, 0.162997, 0.0407574];
beta_LDDRK4 = [0, c_LDDRK4(4)/c_LDDRK4(3), c_LDDRK4(3)/c_LDDRK4(2), c_LDDRK4(2)];


%% Preparing the Domain & Simulation
I_MAX = (X_MAX-X_MIN)/dx;
J_MAX = (Y_MAX-Y_MIN)/dx;
origin_i = -X_MIN/dx;
origin_j = -Y_MIN/dx;

xx = ((0:I_MAX-1)+0.5)*dx+X_MIN;
yy = ((0:J_MAX-1)+0.5)*dx+Y_MIN;
[X,Y] = ndgrid(xx,yy);
theta0 = theta0_deg/180*pi;
Theta = atan2_mod(Y,X);
Theta1 = Theta-theta0;
Theta2 = Theta+theta0;
R = sqrt(X.^2+Y.^2);

I_rcvr = round((X_rcvr-X_MIN)/dx+0.5);
J_rcvr = round((Y_rcvr-Y_MIN)/dx+0.5);
X_rcvr_grid = xx(I_rcvr);
Y_rcvr_grid = yy(J_rcvr);
num_rcvr = length(X_rcvr);

U.px = zeros(I_MAX,J_MAX);
U.py = zeros(I_MAX,J_MAX);
U.u = zeros(I_MAX,J_MAX);
U.v = zeros(I_MAX,J_MAX);
KU.px = zeros(I_MAX,J_MAX);
KU.py = zeros(I_MAX,J_MAX);
KU.u = zeros(I_MAX,J_MAX);
KU.v = zeros(I_MAX,J_MAX);

z0 = rho0*c0;
dt = CFL*dx/c0;         % Timestep size for the simulation
T = t_end-t_start;
N_MAX = round(T/dt);           % Total time steps
tt = (0:N_MAX-1)*dt+t_start;

l = 0;  % Movie frame index


%% Initial Field Calculation
P_inc = zeros(I_MAX,J_MAX);
P_ref = zeros(I_MAX,J_MAX);

P_inc = Heaviside(pi-Theta1).*Signature(t_start+R.*cos(Theta1)/c0,N_duration,N_amplitude,N_slope);
P_ref = Heaviside(pi-Theta2).*Signature(t_start+R.*cos(Theta2)/c0,N_duration,N_amplitude,N_slope);

U.px = (P_inc+P_ref)/2;
U.py = (P_inc+P_ref)/2;
U.u = P_inc/z0*cos(theta0+pi)+P_ref/z0*cos(-theta0+pi);
U.v = P_inc/z0*sin(theta0+pi)+P_ref/z0*sin(-theta0+pi);

% figure(fig1);
% % pcolor(X,Y,Heaviside(pi-Theta1));
% pcolor(X,Y,U.px+U.py);
% xlabel('x [m]'), ylabel('y [m]'), title('p_{initial}');
% colormap(bluered);
% shading flat;
% caxis([-2.0 2.0]);
% colorbar;
% axis image;
% line([0 xx(end)],[0 0],[0 0],'Color','k','LineWidth',2)


%% Propagation
for n = 1:N_MAX
    % LDDRK4
    for m=1:4
        KU.px = U.px+beta_LDDRK4(m)*KU.px;
        KU.py = U.py+beta_LDDRK4(m)*KU.py;
        KU.u = U.u+beta_LDDRK4(m)*KU.u;
        KU.v = U.v+beta_LDDRK4(m)*KU.v;
        KU = EulerPML2D_HalfPlane(KU,CFL,z0,origin_i,origin_j);
    end
    
    U.px = U.px+KU.px;
    U.py = U.py+KU.py;
    U.u = U.u+KU.u;
    U.v = U.v+KU.v;

    % Visualization of the pressure field
    figure(fig2);
    pcolor(X,Y,U.px+U.py);
    xlabel('x [m]'), ylabel('y [m]'), title(['p at t = ',num2str(tt(n))]);
    colormap(bluered);
    shading flat;
    caxis([-2.0 2.0]);
    colorbar;
    axis image;
    line([0 xx(end)],[0 0],[0 0],'Color','k','LineWidth',2)
    
    if mod(tt(n),0.01)<=dt
        figure(fig3);
        pcolor(X,Y,U.px+U.py);
        xlabel('x [m]'), ylabel('y [m]');
        title(['Total field, \theta = ' num2str(theta0_deg) '\circ, t = ' num2str(tt(n)) 's']);
        axis equal, axis([-50 50 -50 50]);
        colormap(bluered);
        shading flat;
        caxis([-2.0 2.0]);
        colorbar;
        line([0 xx(end)],[0 0],[0 0],'Color','k','LineWidth',2)
        l = l+1;
        M_tot(l) = getframe(gcf);
    end
    
    for k=1:num_rcvr
        P_rcvr(k,n) = U.px(I_rcvr(k),J_rcvr(k))+U.py(I_rcvr(k),J_rcvr(k));
    end
end
mkdir('Animations');
movie2avi(M_tot,['./Animations/FDTD_Diffr_HalfPlane_Nwave' num2str(theta0_deg) '_tot.avi'],'compression','Cinepak','fps',5);


%% Save Time Series Data at Receiver Locations
mkdir('Time Series Data');
for k=1:num_rcvr
    fid = fopen(['./Time Series Data/FDTD_' num2str(theta0_deg) '_' num2str(X_rcvr_grid(k)) '_' num2str(Y_rcvr_grid(k)) '.dat'], 'w');
    fprintf(fid, '%f\n', P_rcvr(k,:));
    fclose(fid);
    figure, plot(tt,P_rcvr(k,:));
    xlabel('Time [s]'), ylabel('Normalized Pressure');
    title(['Total field, x=' num2str(X_rcvr_grid(k)) ', y=' num2str(Y_rcvr_grid(k))]);
    axis([min(tt) max(tt) -2 2]);
end
