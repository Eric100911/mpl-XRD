#include <TCanvas.h>
#include <TGraphErrors.h>
#include <TSpectrum.h>
#include <TPolyMarker.h>
#include <TLatex.h>
#include <TFile.h>
#include <TSystem.h>
#include <iostream>
#include <fstream>
#include <string>
#include <TROOT.h>
#include <TStyle.h>
#include <TPaveText.h> // 添加线框支持

// XRD_analysis.C
void XRD_plot(std::string exp_data_file = "exp_data.txt",
              std::string output_image  = "XRD_pattern.png") {
    // 创建TGraphErrors对象存储衍射数据
    TGraphErrors *g = new TGraphErrors(exp_data_file.c_str());
    
    // 设置画布和样式
    TCanvas *c1 = new TCanvas("c1", "X射线多晶衍射谱图", 1200, 800);
    
    // 设置画布边距
    gPad->SetLeftMargin(0.12);    // 增加左侧边距
    gPad->SetRightMargin(0.08);   // 右侧边距
    gPad->SetBottomMargin(0.12);  // 底部边距
    gPad->SetTopMargin(0.08);     // 顶部边距
    gPad->SetGrid(1,1);
    
    gStyle->SetOptStat(0); // 关闭统计信息显示
    
    // 将TGraph转换为TH1D直方图
    Int_t npoints = g->GetN();
    Double_t xmin = g->GetX()[0];
    Double_t xmax = g->GetX()[npoints-1];
    
    // 创建直方图对象
    TH1D *h = new TH1D("h", "", npoints, xmin, xmax);
    
    // 填充直方图数据
    for (Int_t i = 0; i < npoints; i++) {
        h->SetBinContent(i+1, g->GetY()[i]);
    }
    
    // 设置坐标轴标题和单位
    h->GetXaxis()->SetTitle("Diffraction Angle 2#theta (degree)");
    h->GetXaxis()->CenterTitle(true);
    h->GetXaxis()->SetTitleSize(0.05);
    h->GetXaxis()->SetLabelSize(0.04);
    h->GetXaxis()->SetTitleOffset(1.0);
    
    h->GetYaxis()->SetTitle("Diffraction Intensity (a.u.)");
    h->GetYaxis()->CenterTitle(true);
    h->GetYaxis()->SetTitleSize(0.05);
    h->GetYaxis()->SetLabelSize(0.04);
    h->GetYaxis()->SetTitleOffset(1.2);
    
    // 绘制直方图
    h->SetLineColor(kBlue);
    h->SetLineWidth(2);
    h->Draw();
    
    // 自动检测特征峰
    TSpectrum *spec = new TSpectrum(20);
    int npeaks = spec->Search(h, 2, "", 0.007);
    
    double *xpeaks = spec->GetPositionX();
    double *ypeaks = spec->GetPositionY();
    
    // 标记特征衍射峰
    TPolyMarker *pm = new TPolyMarker(npeaks, xpeaks, ypeaks);
    pm->SetMarkerStyle(23);
    pm->SetMarkerColor(kRed);
    pm->SetMarkerSize(1.5);
    pm->Draw();

    // 添加峰位置标签
    TLatex *tex = new TLatex();
    tex->SetTextSize(0.025);
    tex->SetTextColor(kRed);
    tex->SetTextFont(42);
    for (int i=0; i<npeaks; i++) {
        Double_t theta_rad = xpeaks[i] * TMath::Pi() / 360.0;
        Double_t d = 1.5406 / (2 * sin(theta_rad)); // Cu Kα波长
        
        // 使用#theta表示希腊字母θ
        tex->DrawLatex(xpeaks[i] + 1, ypeaks[i], 
                      Form("%.2f#circ", xpeaks[i])); // 仅显示角度值
    }

    // 关键修改：在右上角创建带边框的信息框
    TPaveText *infoBox = new TPaveText(0.65, 0.65, 0.88, 0.88, "NDC");
    infoBox->SetFillColor(0); // 透明背景
    infoBox->SetBorderSize(1); // 边框宽度
    infoBox->SetTextAlign(12); // 左对齐
    infoBox->SetTextSize(0.035);
    
    // 添加实验信息
    infoBox->AddText("X-ray source: ");
    infoBox->AddText("Voltage: 38 kV");
    infoBox->AddText("Current: 30 mA");
    infoBox->AddText("#lambda = 1.5406 #AA (Cu K#alpha)");
    
    // 绘制信息框
    infoBox->Draw();
    
    // 保存图像
    c1->SaveAs(output_image.c_str());
    
    // 清理内存
    delete h;
    delete g;
    delete infoBox;
}