%% Validate_Diffr_HalfPlane_Nwave.m
%
%   written by Sang-Ik Terry Cho
%   last modified on 4 / 11 / 2012
%
%       This program takes the outputs of FDTD_Diffr_HalfPlane_Nwave.m &
%   Analy_Diffr_HalfPlane_Nwave_PtRcvr.m and compares their low frequency 
%   components, below the accuracy limit of the FDTD scheme, given by
%   points-per-wavelength criteron.

clear all, close all;

%% Parameters
% Simulation parameters
dx = 1.0;
theta0_deg = 30;
CFL = 1.0;
c0 = 343;
t_start = -0.1;

% Receiver locations
X_rcvr = [20, 0, -20, 0, 20];
Y_rcvr = [0.01, 20, 0, -20, -0.01];

X_rcvr_grid = (floor(X_rcvr/dx)+0.5)*dx;
Y_rcvr_grid = (floor(Y_rcvr/dx)+0.5)*dx;
num_rcvr = length(X_rcvr);


%% Read Time Series Data
for k = 1:num_rcvr
    Analy_TimeSeries(k,:) = load(['./Time Series Data/Analy_' num2str(theta0_deg) '_' num2str(X_rcvr_grid(k)) '_' num2str(Y_rcvr_grid(k)) '.dat']);
    FDTD_TimeSeries(k,:) = load(['./Time Series Data/FDTD_' num2str(theta0_deg) '_' num2str(X_rcvr_grid(k)) '_' num2str(Y_rcvr_grid(k)) '.dat']);
end

%% Low-pass Filter
N = length(Analy_TimeSeries);
dt = CFL*dx/c0;         % Timestep size for the simulation
tt = (0:N-1)*dt+t_start;
fs = 1/dt;
f_limit = c0/(20*dx);   % The frequency accuracy limit of FDTD scheme based on lambda > 20*dx
f_margin = 2.5;          % The frequency roll off margin on both sides of the crossover frequency
N_filt = 50;          % The FIR filter will be of order (2N_filt-1) with a delay of N_filt samples.

f_trans_lo = f_limit-f_margin;
f_trans_hi = f_limit+f_margin;
f = [0 f_trans_lo f_trans_hi (fs/2)]/(fs/2);
amp_LP = [1 1 0 0];
amp_HP = [0 0 1 1];

% Constructing the linear phase filter
b_LP = firpm(2*(N_filt-1),f,amp_LP,[1 1]);

% Plot Filter Response
freqz_l = 12000;
[h_LP,ff] = freqz(b_LP,1,freqz_l,fs);
figure('Position',[1 100 800 560]);
h = axes('FontSize',16);
plot(ff,20*log10(abs(h_LP)),'LineWidth',2,'Color',[0 0 1]), hold on;
axis([0 200 -50 5]), grid on;
title(['FIR filter Magnitude Response with N_{filt}=' num2str(N_filt)],'fontsize',18);
xlabel('Frequency [Hz]','fontsize',18);
ylabel('Magnitude [dB]','fontsize',18);
legend('Low pass filter','High pass filter','Combined');
set(gcf, 'Color', 'w');
% export_fig filter_mag.tif -a1 -r600 -painters

% Apply Filter
for k = 1:num_rcvr
    Analy_TimeSeries_LP(k,:) = filter(b_LP,1,Analy_TimeSeries(k,:));
    FDTD_TimeSeries_LP(k,:) = filter(b_LP,1,FDTD_TimeSeries(k,:));
end

%% Compare Waveforms
mkdir('Validation Plots');
cd('Validation Plots');
for k = 1:num_rcvr
    % Unfiltered analytical VS filtered analytical
    figure('Position',[0 500 550 400]);
    h = axes('FontSize',16);
    plot(tt,Analy_TimeSeries(k,:),'LineWidth',1.5,'LineStyle','-','Color',[0,0,1]), hold on;
    plot(tt,Analy_TimeSeries_LP(k,:),'LineWidth',1.5,'LineStyle',':','Color',[1,0,0]), hold on;
    xlabel('Time [s]','fontsize',18), ylabel('Pressure','fontsize',18);
    title(['Analytical Solution, x=' num2str(X_rcvr_grid(k)) ', y=' num2str(Y_rcvr_grid(k))],'fontsize',18);
    legend('Original','LP filtered');
    text(0.3,2.1,sprintf('(%c) R%g',char(96+k),k),'FontSize',18);
    axis([min(tt) max(tt) -2.0 2.5]);
    set(gcf, 'Color', 'w');
    export_fig(sprintf('Unfiltered_vs_Filtered_Analy_R%g.png',k),'-a1','-r300','-painters');
    
    % Unfiltered FDTD VS filtered FDTD
    figure('Position',[750 500 550 400]);
    h = axes('FontSize',16);
    plot(tt,FDTD_TimeSeries(k,:),'LineWidth',1.5,'LineStyle','-','Color',[0,0,1]), hold on;
    plot(tt,FDTD_TimeSeries_LP(k,:),'LineWidth',1.5,'LineStyle',':','Color',[1,0,0]), hold on;
    xlabel('Time [s]','fontsize',18), ylabel('Pressure','fontsize',18);
    title(['FDTD Solution, x=' num2str(X_rcvr_grid(k)) ', y=' num2str(Y_rcvr_grid(k))],'fontsize',18);
    legend('Original','LP filtered');
    text(0.3,2.1,sprintf('(%c) R%g',char(96+k),k),'FontSize',18);
    axis([min(tt) max(tt) -2.0 2.5]);
    set(gcf, 'Color', 'w');
    export_fig(sprintf('Unfiltered_vs_Filtered_FDTD_R%g.png',k),'-a1','-r300','-painters');
    
    % Unfiltered analytical VS unfiltered FDTD
    figure('Position',[0 0 550 400]);
    h = axes('FontSize',16);
    plot(tt,Analy_TimeSeries(k,:),'LineWidth',1.5,'LineStyle','-','Color',[0,0,1]), hold on;
    plot(tt,FDTD_TimeSeries(k,:),'LineWidth',1.5,'LineStyle',':','Color',[1,0,0]), hold on;
    xlabel('Time [s]','fontsize',18), ylabel('Pressure','fontsize',18);
%     title(['Unfiltered Analytical & FDTD Solutions, x=' num2str(X_rcvr_grid(k)) ', y=' num2str(Y_rcvr_grid(k))],'fontsize',18);
    legend('Analytical','FDTD');
    text(0.3,2.1,sprintf('(%c) R%g',char(96+k),k),'FontSize',18);
    axis([min(tt) max(tt) -2.0 2.5]);
    set(gcf, 'Color', 'w');
    export_fig(sprintf('Unfiltered_Analy_vs_FDTD_R%g.png',k),'-a1','-r300','-painters');

    % Filtered analytical VS filtered FDTD
    figure('Position',[750 0 550 400]);
    h = axes('FontSize',16);
    plot(tt,Analy_TimeSeries_LP(k,:),'LineWidth',1.5,'LineStyle','-','Color',[0,0,1]), hold on;
    plot(tt,FDTD_TimeSeries_LP(k,:),'LineWidth',1.5,'LineStyle',':','Color',[1,0,0]), hold on;
    xlabel('Time [s]','fontsize',18), ylabel('Pressure','fontsize',18);
%     title(['Low-pass Filtered Analytical & FDTD Solution, x=' num2str(X_rcvr_grid(k)) ', y=' num2str(Y_rcvr_grid(k))],'fontsize',18);
    legend('Analytical','FDTD');
    text(0.3,2.1,sprintf('(%c) R%g',char(96+k),k),'FontSize',18);
    axis([min(tt) max(tt) -2.0 2.5]);
    set(gcf, 'Color', 'w');
    export_fig(sprintf('Filtered_Analy_vs_FDTD_R%g.png',k),'-a1','-r300','-painters');
end

cd('..');
close all;