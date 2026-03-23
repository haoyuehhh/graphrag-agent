import os
import sys
import subprocess

print('='*60)
print('🔍 Tech Radar Agent 项目健康检查')
print('='*60)

# 1. 结构检查
print('\n📁 1. 项目结构')
required = [
    'app/core/mcp/protocol.py',
    'app/core/mcp/server.py', 
    'app/core/mcp/client.py',
    'app/core/skills/base.py',
    'app/core/skills/registry.py',
    'app/core/skills/implementations/browser_skill.py',
    'app/services/competitor_analyzer.py',
    'app/api/v1/endpoints/competitors.py',
    'app/models/competitor_schemas.py',
    'graph_store.py',
    'app/main.py',
    'README.md'
]
missing = [f for f in required if not os.path.exists(f)]
print(f'  核心文件: {len(required)-len(missing)}/{len(required)}')
if missing:
    print(f'  ❌ 缺失: {missing}')

# 2. 语法检查
print('\n🐍 2. 语法检查')
import py_compile
errors = []
for f in required:
    if os.path.exists(f):
        try:
            py_compile.compile(f, doraise=True)
        except Exception as e:
            errors.append(f'{f}: {str(e)[:30]}')
print(f'  错误: {len(errors)}个' + (f'\n  {errors[0]}' if errors else ' ✅'))

# 3. 导入测试
print('\n📦 3. 模块导入')
try:
    from app.core.mcp import MCPServer, MCPClient
    print('  ✅ MCP模块')
except Exception as e:
    print(f'  ❌ MCP: {e}')
    
try:
    from app.core.skills import SkillRegistry
    print('  ✅ Skill系统')
except Exception as e:
    print(f'  ❌ Skill: {e}')
    
try:
    from app.services.competitor_analyzer import competitor_analyzer
    print('  ✅ 竞品分析器')
except Exception as e:
    print(f'  ❌ 分析器: {e}')

# 4. FastAPI检查
print('\n🚀 4. FastAPI应用')
try:
    from app.main import app
    routes = [r.path for r in app.routes if hasattr(r, 'path')]
    competitor = [r for r in routes if 'competitor' in r.lower()]
    skills = [r for r in routes if 'skill' in r.lower()]
    print(f'  ✅ 应用加载')
    print(f'  竞品端点: {len(competitor)}个 {competitor[:2]}')
    print(f'  Skill端点: {len(skills)}个 {skills[:1]}')
except Exception as e:
    print(f'  ❌ 应用加载失败: {e}')
    sys.exit(1)

# 5. 功能测试
print('\n🧪 5. API功能测试')
try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    health = client.get('/api/v1/health/health')
    print(f'  健康检查: {health.status_code} ✅' if health.status_code == 200 else f'  健康检查: {health.status_code} ❌')
    
    matrix = client.get('/api/v1/competitors/matrix/features')
    print(f'  竞品矩阵: {matrix.status_code} ✅' if matrix.status_code == 200 else f'  竞品矩阵: {matrix.status_code} ❌')
    
    compare = client.post('/api/v1/competitors/compare', json={'competitor_names': ['Notion'], 'dimension': 'features'})
    print(f'  对比接口: {compare.status_code} ✅' if compare.status_code in [200, 422] else f'  对比接口: {compare.status_code} ❌')
except Exception as e:
    print(f'  ⚠️ 测试异常: {str(e)[:50]}')

# 6. 数据目录
print('\n💾 6. 数据层')
print(f'  data目录: {"✅" if os.path.exists("data") else "❌"}')
print(f'  graph_db: {"✅" if os.path.exists("graph_db") else "❌"}')

# 7. Git状态
print('\n📊 7. Git状态')
try:
    status = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True)
    log = subprocess.run(['git', 'log', '--oneline', '-1'], capture_output=True, text=True)
    if status.stdout.strip():
        print(f'  ⚠️ 未提交: {len(status.stdout.strip().split(chr(10)))}个文件')
    else:
        print('  ✅ 工作区干净')
    print(f'  📌 {log.stdout.strip()}')
except Exception as e:
    print(f'  ⚠️ Git检查失败')

print('\n' + '='*60)
print('✅ 检查完成')
print('='*60)