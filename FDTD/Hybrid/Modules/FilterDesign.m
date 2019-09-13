function [b_LP,b_HP] = FilterDesign(fs,f_crossover,f_margin,N_filt)
%% FilterDesign.m
%
%   written by:     Sang-Ik Cho
%   last modified:  7 / 22 / 11
%
%       This script uses 'firpm' function to designs a Parks-McClellan FIR 
%   filter pair according to an arbitrary filter magnitude and user 
%   specified sampling frequency, crossover frequency and filter 
%   coefficient length.  The calculated filter coefficients are returned 
%   and can then be used by other scripts.

% clear all, close all;
% scrsz = get(0,'ScreenSize');

% Arbitrary magnitude response
f_trans_lo = f_crossover-f_margin;
f_trans_hi = f_crossover+f_margin;
f = [0 f_trans_lo f_trans_hi (fs/2)]/(fs/2);
amp_LP = [1 1 0 0];
amp_HP = [0 0 1 1];

% Constructing the linear phase filter
b_LP = firpm(2*(N_filt-1),f,amp_LP,[1 1]);
b_HP = firpm(2*(N_filt-1),f,amp_HP,[1 1]);

% % Plot
% freqz_l = 12000;
% [h_LP,ff] = freqz(b_LP,1,freqz_l,fs);
% [h_HP,ff] = freqz(b_HP,1,freqz_l,fs);
% figure('Position',[1 100 800 560]);
% h = axes('FontSize',16);
% plot(ff,20*log10(abs(h_LP)),'LineWidth',2,'Color',[0 0 1]), hold on;
% plot(ff,20*log10(abs(h_HP)),'LineWidth',2,'Color',[1 0 0]), hold on;
% plot(ff,20*log10(abs(h_LP+h_HP)),'LineWidth',2,'Color',[0.7 0.9 0.2]), hold on;
% axis([0 200 -50 5]), grid on;
% title(['FIR filter Magnitude Response with N_{filt}=' num2str(N_filt)],'fontsize',18);
% xlabel('Frequency [Hz]','fontsize',18);
% ylabel('Magnitude [dB]','fontsize',18);
% legend('Low pass filter','High pass filter','Combined');
% set(gcf, 'Color', 'w');
% export_fig filter_mag.tif -a1 -r600 -painters

