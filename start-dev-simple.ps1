# GraphRAG 开发环境启动脚本 - 简化版

Write-Host "=========================================="
Write-Host "GraphRAG 开发环境启动脚本 (简化版)"
Write-Host "=========================================="

# 检查Python是否安装
try {
    $pythonVersion = python --version
    Write-Host "Python版本: $pythonVersion"
}
catch {
    Write-Host "错误：Python未安装或不在PATH中"
    Write-Host "请先安装Python并添加到PATH"
    exit 1
}

# 检查Node.js是否安装
try {
    $nodeVersion = node --version
    Write-Host "Node.js版本: $nodeVersion"
}
catch {
    Write-Host "错误：Node.js未安装或不在PATH中"
    Write-Host "请先安装Node.js并添加到PATH"
    exit 1
}

# 获取脚本所在目录（项目根目录）
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

Write-Host ""
Write-Host "项目根目录: $projectRoot"
Write-Host ""

# 启动后端服务
Write-Host "正在启动后端服务..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$projectRoot'; python -m app.main"

# 等待后端启动
Write-Host "等待后端启动 (3秒)..."
Start-Sleep -Seconds 3

# 启动前端服务
Write-Host "正在启动前端服务..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$projectRoot\frontend'; npm run dev"

Write-Host ""
Write-Host "=========================================="
Write-Host "服务启动完成！"
Write-Host "后端地址: http://localhost:8000"
Write-Host "前端地址: http://localhost:5173"
Write-Host "API文档: http://localhost:8000/docs"
Write-Host "=========================================="
Write-Host ""
Write-Host "按任意键退出此窗口（服务将继续运行）..."
$null = [System.Console]::ReadKey()