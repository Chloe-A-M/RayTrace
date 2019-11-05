function Analy_Diffr_HalfPlane_Nwave_PtRcvr()
%% Analy_Diffr_HalfPlane_Nwave_PtRcvr.m
%
%   written by Sang-Ik Terry Cho
%   last modified on 1 / 11 / 2012
%
%       This program plots an analytical closed-form solution of a 2-D 
%   half plane diffraction problem found in Hewett (2011).  The solution
%   is for an incoming plane wave of a perfect N-wave.
%       The example case presented in this program models a rigid half
%   plane, which corresponds to dp/dn = 0 on the boundary.  The half plane
%   lies on the (+)ve x-axis starting at the origin and the radial angle is
%   defined going counterclockwise from the (+)ve x-axis.
%       The pressure time series is calculated at the receiver location 
%   specified by the user and is plotted.
%
%   *** NOTE: The integral expression fails to produce analytic solution at
%   locations for which the Theta0 value becomes multiples of pi/4. ***

clear all, close all;

%% Parameters
% Receiver location
x_rcvr = 0.5;
y_rcvr = -19.5;

% Domain parameters
dx = 1;

% Time parameters
CFL = 1.0;
c0 = 343;
t_start = -0.2;
t_end = 0.8;

% Incoming signature parameters
N_duration = 0.5;
N_amplitude = 1;
N_slope = N_duration/2/N_amplitude;
theta0_deg = 120;

% Simulatiom parameter
reltol = 1e-6;


%% Preparing the domain
dt = CFL*dx/c0;         % Timestep size for the simulation
N = round((t_end-t_start)/dt);
tt = (0:N-1)*dt+t_start;

theta0 = theta0_deg/180*pi;
Theta = atan2_mod(y_rcvr,x_rcvr);
Theta1 = Theta-theta0;
Theta2 = Theta+theta0;
R = sqrt(x_rcvr^2+y_rcvr^2);

P_inc = zeros(1,N);
P_ref = zeros(1,N);
P_dif1 = zeros(1,N);
P_dif2 = zeros(1,N);


%% Propagation
for n = 1:N
    P_inc(n) = Heaviside(pi-Theta1)*Heaviside(tt(n)+R*cos(Theta1)/c0)*Signature(tt(n)+R*cos(Theta1)/c0);
    P_ref(n) = Heaviside(pi-Theta2)*Heaviside(tt(n)+R*cos(Theta2)/c0)*Signature(tt(n)+R*cos(Theta2)/c0);

    if tt(n)-R/c0 >= 0  % replacing Heaviside(tt(n)-R/c)
        Integrand1 = @(S)Signature(tt(n)-R/c0-S)./(sqrt(S).*(S+R/c0*(1+cos(Theta1))));
        Integrand2 = @(S)Signature(tt(n)-R/c0-S)./(sqrt(S).*(S+R/c0*(1+cos(Theta2))));
        P_dif1(n) = -sign(pi-Theta1)*sqrt(R/c0*(1+cos(Theta1)))/(2*pi)*Heaviside(tt(n)-R/c0)*quadgk(Integrand1,0,tt(n)-R/c0,'RelTol',reltol);
        P_dif2(n) = -sign(pi-Theta2)*sqrt(R/c0*(1+cos(Theta2)))/(2*pi)*Heaviside(tt(n)-R/c0)*quadgk(Integrand2,0,tt(n)-R/c0,'RelTol',reltol);
    end
end
P_tot = P_inc+P_ref+P_dif1+P_dif2;


%% Plot of Time Series
scrsz = get(0,'ScreenSize');
figure('Position',[1 scrsz(4)/2-100 scrsz(3) scrsz(4)/2])
subplot(1,3,1);plot(tt,P_inc+P_ref), axis([min(tt) max(tt) -2 2]);
xlabel('Time [s]'), ylabel('Normalized Pressure');
title(['Inc+Ref fields, x=' num2str(x_rcvr), ', y=' num2str(y_rcvr)])
subplot(1,3,2);plot(tt,P_dif1+P_dif2), axis([min(tt) max(tt) -2 2]);
xlabel('Time [s]'), ylabel('Normalized Pressure');
title(['Diffracted field, x=' num2str(x_rcvr), ', y=' num2str(y_rcvr)])
subplot(1,3,3);plot(tt,P_tot), axis([min(tt) max(tt) -2 2]);
xlabel('Time [s]'), ylabel('Normalized Pressure');
title(['Total field, x=' num2str(x_rcvr), ', y=' num2str(y_rcvr)])


%% Save Time Series Data
mkdir('Time Series Data');
fid = fopen(['./Time Series Data/Analy_' num2str(theta0_deg) '_' num2str(x_rcvr) '_' num2str(y_rcvr) '.dat'], 'w');
fprintf(fid, '%f\n', P_tot);
fclose(fid);


%% Functions
function Theta = atan2_mod(X,Y)
    Theta = atan2(X,Y);
    I = find(Theta<0);
    Theta(I) = Theta(I)+2*pi;
end

function X = Heaviside(x)
    X = ones(size(x));
    I = find(x<0);
    X(I) = 0;
end
function res = Signature(S)
    res = Heaviside(S).*Heaviside(N_duration-S).*(N_amplitude-S/N_slope);
end

end