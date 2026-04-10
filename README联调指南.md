# GraphRAG项目前后端联调方案（PowerShell兼容版）

## 项目结构说明

- **后端**：位于 `app/` 目录，使用Python + FastAPI开发，入口文件为 `app/main.py`
- **前端**：位于 `frontend/` 目录，使用React + TypeScript + Vite开发
- **项目根目录**：`e:/graphrag-agent`

## 后端启动命令及验证方式

### 启动命令（PowerShell）
```powershell
cd app; python main.py
```

### 验证方式
- 后端运行在 `http://localhost:8000`（默认端口）
- 可以通过访问 `http://localhost:8000/health` 检查服务状态
- API文档通常在 `http://localhost:8000/docs`（如果使用FastAPI）

## 前端启动命令及访问地址

### 开发环境启动（PowerShell）
```powershell
cd frontend; npm run dev
```

### 访问地址
- 前端开发服务器运行在 `http://localhost:5173`
- 通过Vite代理配置自动转发API请求到后端

### 生产环境构建（PowerShell）
```powershell
cd frontend; npm run build
```

## 代理配置确认

在 `frontend/vite.config.ts` 中已配置代理：
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

### 代理规则：
- 前端请求 `/api/*` 路径会被代理到后端 `http://localhost:8000/*`
- 例如：前端请求 `/api/knowledge` 会被转发到 `http://localhost:8000/knowledge`

## 联调测试步骤

### 1. 启动后端服务（PowerShell）
```powershell
cd app; python main.py
```

### 2. 启动前端开发服务器（PowerShell）
```powershell
cd frontend; npm run dev
```

### 3. 访问前端应用
打开浏览器访问：`http://localhost:5173`

### 4. 测试API连接
- 在前端控制台中检查网络请求
- 确认 `/api/*` 请求成功转发到后端
- 验证数据能否正确获取和显示

### 5. 调试和问题排查
- 检查浏览器控制台错误
- 查看后端日志输出
- 确认端口是否冲突

## 关键注意事项

### 端口配置：
- 后端：8000（默认）
- 前端开发：5173（Vite默认）
- 确保端口未被占用

### API路径规范：
- 前端使用 `/api/` 前缀
- 后端提供对应的API路由

### 环境变量：
- 检查 `.env` 文件中的配置
- 确保前后端环境一致

### 依赖安装：
- 确保前后端依赖都已正确安装
- 运行 `npm install` 和 `pip install -r requirements.txt`

## 当前状态检查

✅ 已完成：
- 后端入口文件确认（app/main.py）
- 前端代理配置已添加（vite.config.ts）
- 前端构建脚本确认（package.json）

🔄 待确认：
- 前端dist构建产物存在性（需要执行构建）
- 实际联调测试

## 故障排除指南

### 常见问题及解决方案

1. **端口冲突**
   ```powershell
   # 检查端口占用
   netstat -ano | findstr :8000
   netstat -ano | findstr :5173
   
   # 如果端口被占用，可以修改配置
   # 后端：修改 app/main.py 中的端口
   # 前端：修改 frontend/vite.config.ts 中的代理目标
   ```

2. **API请求失败**
   ```powershell
   # 检查后端是否正常运行
   curl http://localhost:8000/health
   
   # 检查代理配置
   # 确认 vite.config.ts 中的 target 地址正确
   ```

3. **CORS跨域问题**
   - 后端已配置CORS中间件，允许跨域请求
   - 如果仍有问题，检查后端CORS配置

4. **依赖安装问题**
   ```powershell
   # 后端依赖
   cd app; pip install -r requirements.txt
   
   # 前端依赖
   cd frontend; npm install
   ```

## 自动化脚本（可选）

可以创建PowerShell脚本来自动化联调过程：

```powershell
# start-dev.ps1
Write-Host "启动GraphRAG开发环境..."
Write-Host "1. 启动后端服务..."
Start-Process -FilePath "python" -ArgumentList "main.py" -WorkingDirectory "app" -NoNewWindow

# 等待后端启动
Start-Sleep -Seconds 5

Write-Host "2. 启动前端开发服务器..."
Start-Process -FilePath "npm" -ArgumentList "run dev" -WorkingDirectory "frontend"

Write-Host "开发环境已启动！"
Write-Host "后端: http://localhost:8000"
Write-Host "前端: http://localhost:5173"
```

## 验证联调成功

1. 访问前端应用：`http://localhost:5173`
2. 打开浏览器开发者工具
3. 查看Network标签页
4. 确认 `/api/*` 请求状态为200
5. 检查响应数据是否正确

这个联调方案确保前后端能够无缝协作，通过Vite代理实现开发环境的API请求转发，提高开发效率。后端还配置了CORS中间件，允许跨域请求，进一步简化了前后端联调过程。