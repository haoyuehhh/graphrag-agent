# GraphRAG 开发环境启动脚本
# PowerShell兼容版 - 改进版

param(
    [switch]$DebugMode,
    [switch]$CleanStart,
    [switch]$SkipBackend,
    [switch]$SkipFrontend,
    [switch]$ShowLogs
)

Write-Host "=========================================="
Write-Host "GraphRAG 开发环境启动脚本 (改进版)"
Write-Host "=========================================="

# 配置
$backendPort = 8000
$frontendPort = 5173
$backendTimeout = 30  # 后端启动超时时间（秒）
$backendCheckInterval = 2  # 检查间隔（秒）

# 函数：显示帮助信息
function Show-Help {
    Write-Host "用法: ./start-dev.ps1 [参数]"
    Write-Host ""
    Write-Host "参数:"
    Write-Host "  -DebugMode    启用调试模式，显示详细日志"
    Write-Host "  -CleanStart   清理并重新启动服务"
    Write-Host "  -SkipBackend  跳过后端服务启动"
    Write-Host "  -SkipFrontend 跳过前端服务启动" 
    Write-Host "  -ShowLogs     显示服务日志"
    Write-Host ""
}

# 函数：检查端口是否被占用（PowerShell原生方法）
function Test-PortInUse {
    param([int]$port)
    
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Any, $port)
        $listener.Start()
        $listener.Stop()
        return $false
    }
    catch {
        return $true
    }
}

# 函数：清理进程
function Clean-Processes {
    param([string]$processName)
    
    $processes = Get-Process -Name $processName -ErrorAction SilentlyContinue
    if ($processes) {
        Write-Host "正在清理 $processName 进程..."
        $processes | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
}

# 函数：检查服务是否启动
function Test-ServiceStarted {
    param([string]$url, [int]$timeout)
    
    $startTime = Get-Date
    $endTime = $startTime.AddSeconds($timeout)
    
    while ($true) {
        try {
            $response = Invoke-WebRequest -Uri $url -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
            if ($response -and $response.StatusCode -eq 200) {
                return $true
            }
        }
        catch {
            if ((Get-Date) -gt $endTime) {
                return $false
            }
        }
        Start-Sleep -Seconds $backendCheckInterval
    }
}

# 检查参数
if ($DebugMode) {
    $global:DebugPreference = "Continue"
}

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

# 检查npm是否安装
try {
    $npmVersion = npm --version
    Write-Host "npm版本: $npmVersion"
}
catch {
    Write-Host "错误：npm未安装或不在PATH中"
    Write-Host "请先安装npm并添加到PATH"
    exit 1
}

# 获取脚本所在目录（项目根目录）
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

Write-Host ""
Write-Host "项目根目录: $projectRoot"
Write-Host ""

# 清理启动（如果指定）
if ($CleanStart) {
    Write-Host "清理现有服务..."
    Clean-Processes "python"
    Clean-Processes "node"
    Write-Host "清理完成"
}

# 检查端口占用
if (Test-PortInUse $backendPort) {
    Write-Host "警告：端口 $backendPort 已被占用，后端服务可能无法启动"
}
if (Test-PortInUse $frontendPort) {
    Write-Host "警告：端口 $frontendPort 已被占用，前端服务可能无法启动"
}

# 启动后端服务
if (-not $SkipBackend) {
    Write-Host "正在启动后端服务..."
    
    # 检查requirements.txt是否存在并安装依赖
    $requirementsPath = Join-Path $projectRoot "requirements.txt"
    if (Test-Path $requirementsPath) {
        Write-Host "正在安装Python依赖..."
        try {
            python -m pip install -r $requirementsPath --quiet
            Write-Host "Python依赖安装完成"
        }
        catch {
            Write-Host "警告：Python依赖安装失败，但将继续启动服务"
        }
    }
    
    # 启动后端进程
    $backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$projectRoot'; python -m app.main" -PassThru
    
    # 等待后端启动
    Write-Host "等待后端启动 ($backendTimeout 秒)..."
    $backendUrl = "http://localhost:$backendPort"
    
    if (Test-ServiceStarted $backendUrl $backendTimeout) {
        Write-Host "后端服务启动成功"
    }
    else {
        Write-Host "错误：后端服务启动超时"
        $backendProcess | Stop-Process -Force -ErrorAction SilentlyContinue
        exit 1
    }
}
else {
    Write-Host "跳过后端服务启动（-SkipBackend 参数）"
}

# 启动前端服务
if (-not $SkipFrontend) {
    Write-Host "正在启动前端服务..."
    
    # 检查并安装前端依赖
    $frontendPath = Join-Path $projectRoot "frontend"
    if (Test-Path $frontendPath) {
        Set-Location $frontendPath
        
        # 检查package.json是否存在
        $packageJsonPath = Join-Path $frontendPath "package.json"
        if (Test-Path $packageJsonPath) {
            # 检查node_modules是否存在
            $nodeModulesPath = Join-Path $frontendPath "node_modules"
            if (-not (Test-Path $nodeModulesPath)) {
                Write-Host "正在安装前端依赖..."
                try {
                    npm install --silent
                    Write-Host "前端依赖安装完成"
                }
                catch {
                    Write-Host "警告：前端依赖安装失败，但将继续启动服务"
                }
            }
        }
        
        Set-Location $projectRoot
    }
    
    # 启动前端进程
    $frontendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$frontendPath'; npm run dev" -PassThru
    
    # 启动前端进程
    $frontendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$frontendPath'; npm run dev" -PassThru
    
    # 简单等待前端启动
    Start-Sleep -Seconds 5
    
    # 检查前端是否启动
    $frontendUrl = "http://localhost:$frontendPort"
    try {
        $response = Invoke-WebRequest -Uri $frontendUrl -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response -and $response.StatusCode -eq 200) {
            Write-Host "前端服务启动成功"
        }
        else {
            Write-Host "警告：前端服务可能已启动，但无法验证"
        }
    }
    catch {
        Write-Host "警告：无法验证前端服务状态"
    }
}
else {
    Write-Host "跳过前端服务启动（-SkipFrontend 参数）"
}

Write-Host ""
Write-Host "=========================================="
Write-Host "服务启动完成！"
Write-Host "后端地址: http://localhost:$backendPort"
Write-Host "前端地址: http://localhost:$frontendPort"
Write-Host "API文档: http://localhost:$backendPort/docs"
Write-Host "=========================================="

# 显示日志（如果指定）
if ($ShowLogs) {
    Write-Host "按任意键继续..."
    $null = [System.Console]::ReadKey()
}

Write-Host ""
Write-Host "按任意键退出此窗口（服务将继续运行）..."
$null = [System.Console]::ReadKey()