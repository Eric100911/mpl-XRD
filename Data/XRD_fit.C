#include "TFile.h"
#include "TGraphErrors.h"
#include "TF1.h"
#include "TCanvas.h"
#include "TMultiGraph.h"
#include "TLegend.h"
#include "TMath.h"
#include "TStyle.h"
#include "TLatex.h"
#include <fstream>
#include <sstream>
#include <vector>
#include <map>
#include <iostream>
#include <algorithm>
#include <cctype>
#include <cmath>

struct XRDTable {
    std::string caption;
    std::string label;
    std::vector<std::vector<std::string>> data;
};

// Nelson-Riley 函数
double nelsonRiley(double theta) {
    double thetaRad = theta * TMath::Pi() / 180.0;
    double sinTheta = TMath::Sin(thetaRad);
    double cos2Theta = TMath::Cos(thetaRad) * TMath::Cos(thetaRad);
    return 0.5 * (cos2Theta / sinTheta + cos2Theta / thetaRad);
}

// 从LaTeX文件中提取所有表格数据
std::vector<XRDTable> extractTablesFromLatex(const std::string& filename) {
    std::vector<XRDTable> tables;
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error: Could not open file " << filename << std::endl;
        return tables;
    }
    
    std::string line;
    XRDTable currentTable;
    bool inTable = false;
    bool inTabular = false;
    bool headerPassed = false;
    int columnCount = 5; // 固定为5列，根据报告表格格式
    
    while (std::getline(file, line)) {
        // 检测表格开始
        if (line.find("\\begin{table}") != std::string::npos) {
            inTable = true;
            currentTable = XRDTable(); // 重置当前表格
            continue;
        }
        
        // 检测表格结束
        if (line.find("\\end{table}") != std::string::npos && inTable) {
            inTable = false;
            inTabular = false;
            tables.push_back(currentTable);
            continue;
        }
        
        // 提取表格标题
        if (inTable && line.find("\\caption{") != std::string::npos) {
            size_t start = line.find("{") + 1;
            size_t end = line.find("}", start);
            if (end != std::string::npos) {
                currentTable.caption = line.substr(start, end - start);
            }
        }
        
        // 提取表格标签
        if (inTable && line.find("\\label{") != std::string::npos) {
            size_t start = line.find("{") + 1;
            size_t end = line.find("}", start);
            if (end != std::string::npos) {
                currentTable.label = line.substr(start, end - start);
            }
        }
        
        // 检测tabular开始
        if (inTable && line.find("\\begin{tabular}") != std::string::npos) {
            inTabular = true;
            headerPassed = false;
            continue;
        }
        
        // 检测tabular结束
        if (inTabular && line.find("\\end{tabular}") != std::string::npos) {
            inTabular = false;
            continue;
        }
        
        if (inTabular) {
            // 跳过表头行和规则行
            if (!headerPassed) {
                if (line.find("\\midrule") != std::string::npos || 
                    line.find("\\hline") != std::string::npos) {
                    headerPassed = true;
                }
                continue;
            }
            
            // 跳过表格结束行
            if (line.find("\\bottomrule") != std::string::npos || 
                line.find("\\toprule") != std::string::npos) {
                continue;
            }
            
            // 手动解析表格行
            std::vector<std::string> row;
            std::string cell;
            bool inCell = false;
            
            for (char c : line) {
                if (c == '&') {
                    // 移除空格和LaTeX命令
                    cell.erase(std::remove(cell.begin(), cell.end(), ' '), cell.end());
                    if (!cell.empty()) {
                        row.push_back(cell);
                    }
                    cell.clear();
                    inCell = false;
                } else if (c == '\\' || c == '$' || c == ' ' || c == '\t') {
                    // 跳过LaTeX特殊字符和空白
                    continue;
                } else if (c == '{' || c == '}') {
                    // 跳过花括号
                    continue;
                } else {
                    cell += c;
                    inCell = true;
                }
            }
            
            // 处理最后一个单元格
            if (!cell.empty()) {
                row.push_back(cell);
            }
            
            // 确保有5列数据
            if (row.size() == columnCount) {
                // 特别处理晶面指数中的逗号和括号
                if (row[2].find("(") != std::string::npos) {
                    size_t start = row[2].find("(") + 1;
                    size_t end = row[2].find(")");
                    if (end != std::string::npos) {
                        row[2] = row[2].substr(start, end - start);
                        // 替换逗号为空格
                        std::replace(row[2].begin(), row[2].end(), ',', ' ');
                    }
                }
                
                currentTable.data.push_back(row);
            }
        }
    }
    
    return tables;
}

double calculateRSquared(TGraphErrors* gr, TF1* fitFunc) {
    double ss_res = 0.0;
    double ss_tot = 0.0;
    double y_mean = 0.0;
    
    // 计算y的均值
    for (int i = 0; i < gr->GetN(); i++) {
        double x, y;
        gr->GetPoint(i, x, y);
        y_mean += y;
    }
    y_mean /= gr->GetN();
    
    // 计算残差平方和(SSres)和总平方和(SStot)
    for (int i = 0; i < gr->GetN(); i++) {
        double x, y;
        gr->GetPoint(i, x, y);
        double y_pred = fitFunc->Eval(x);
        ss_res += (y - y_pred) * (y - y_pred);
        ss_tot += (y - y_mean) * (y - y_mean);
    }
    
    // 计算R²
    return 1.0 - (ss_res / ss_tot);
}


// 执行Nelson-Riley拟合
void performNelsonRileyFit(const std::vector<XRDTable>& tables) {
    if (tables.empty()) {
        std::cerr << "Error: No tables found in LaTeX file!" << std::endl;
        return;
    }
    
    TMultiGraph *multiGraph = new TMultiGraph();
    TLegend *legend = new TLegend(0.7, 0.7, 0.9, 0.9);
    std::vector<TF1*> fitFunctions;
    std::map<std::string, double> trueAValues; // 存储每个表格的真实晶格常数
    
    int colorIndex = 1;
    const int nColors = 8;
    int colors[nColors] = {kBlack, kRed, kBlue, kGreen+2, kMagenta+1, kCyan+1, kOrange+1, kYellow+2};
    
    for (const auto& table : tables) {
        // 只处理包含晶格常数的表格
        if (table.data.empty() || table.data[0].size() < 5) {
            std::cout << "Skipping table '" << table.caption << "' - insufficient data" << std::endl;
            continue;
        }
        
        // 创建用于绘图的数组
        const int n = table.data.size();
        std::vector<double> x(n), y(n), ex(n), ey(n);
        int validPoints = 0;
        
        // 计算Nelson-Riley函数值和晶格常数
        for (int i = 0; i < n; ++i) {
            try {
                double theta = std::stod(table.data[i][0]) / 2.0; // 2θ → θ
                double a = std::stod(table.data[i][4]); // 晶格常数
                
                x[validPoints] = nelsonRiley(theta);
                y[validPoints] = a;
                ex[validPoints] = 0;
                ey[validPoints] = 0.001; // y方向误差估计值
                validPoints++;
            } catch (const std::invalid_argument& e) {
                std::cerr << "Invalid data in table '" << table.caption << "', row " << i << ": " << e.what() << std::endl;
            } catch (const std::out_of_range& e) {
                std::cerr << "Out of range data in table '" << table.caption << "', row " << i << ": " << e.what() << std::endl;
            }
        }
        
        if (validPoints < 2) {
            std::cout << "Skipping table '" << table.caption << "' - insufficient valid points (" << validPoints << ")" << std::endl;
            continue;
        }
        
        // 创建TGraphErrors（带误差棒）
        TGraphErrors *gr = new TGraphErrors(validPoints, x.data(), y.data(), ex.data(), ey.data());
        gr->SetTitle("");
        gr->SetMarkerStyle(20);       // 圆点
        gr->SetMarkerColor(kBlack);   // 黑色数据点
        gr->SetLineColor(kBlack);      // 黑色误差棒

        // 创建线性拟合函数（红色实线）
        TF1 *fitFunc = new TF1(("fitFunc_" + table.label).c_str(), "[0] + [1]*x", 0, 1);
        fitFunc->SetLineColor(kRed);   // 红色拟合线
        fitFunc->SetLineStyle(1);      // 实线
        
        // 执行拟合
        gr->Fit(fitFunc, "Q");
        
        // 计算R²值
        double rSquared = calculateRSquared(gr, fitFunc);

        // 创建单独画布
        TCanvas *canvas = new TCanvas(("c_" + table.label).c_str(), 
                                     ("Nelson-Riley Fit: " + table.caption).c_str(), 
                                     800, 600);
        gPad->SetGrid();
        
        // 绘制图形
        gr->Draw("AP");      // 带误差棒的数据点
        fitFunc->Draw("SAME"); // 红色拟合线
        
        // 添加标注
        TLatex latex;
        latex.SetNDC();
        latex.SetTextSize(0.03);
        latex.DrawLatex(0.15, 0.85, Form("True Lattice Constant: %.4f #pm %.4f #AA", 
                                         fitFunc->GetParameter(0), fitFunc->GetParError(0)));
        latex.DrawLatex(0.15, 0.80, Form("R^{2} = %.4f", rSquared));
        
        // 保存为单独PDF
        std::string filename = "Fit_" + table.label + ".png";
        canvas->SaveAs(filename.c_str());
        
        // 清理当前拟合资源
        delete canvas;
        delete gr;
        delete fitFunc;
    }
}

void XRD_fit(const char* filename = "experiment_report.tex") {
    // 从LaTeX文件中提取所有表格
    auto tables = extractTablesFromLatex(filename);
    
    // 执行Nelson-Riley拟合
    performNelsonRileyFit(tables);
}
