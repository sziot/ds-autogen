#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🧪 检查前端运行环境...\n');

// 检查 Node.js 版本
try {
  const nodeVersion = process.version;
  const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0]);
  
  console.log(`✅ Node.js 版本: ${nodeVersion}`);
  
  if (majorVersion < 18) {
    console.error(`❌ 需要 Node.js 18 或更高版本，当前版本: ${nodeVersion}`);
    process.exit(1);
  }
} catch (error) {
  console.error('❌ 无法检查 Node.js 版本:', error.message);
  process.exit(1);
}

// 检查包管理器
const packageManagers = {
  'package-lock.json': 'npm',
  'yarn.lock': 'yarn',
  'pnpm-lock.yaml': 'pnpm'
};

let packageManager = 'npm';
for (const [file, pm] of Object.entries(packageManagers)) {
  if (fs.existsSync(file)) {
    packageManager = pm;
    break;
  }
}

console.log(`✅ 包管理器: ${packageManager}`);

// 检查依赖安装
if (!fs.existsSync('node_modules')) {
  console.warn('⚠️  node_modules 不存在，请运行安装命令:');
  console.log(`   ${packageManager} install`);
  process.exit(1);
} else {
  console.log('✅ 依赖已安装');
}

// 检查环境变量文件
const envFiles = ['.env.development', '.env.production', '.env.test'];
let missingEnvFiles = [];

envFiles.forEach(file => {
  if (!fs.existsSync(file)) {
    missingEnvFiles.push(file);
  }
});

if (missingEnvFiles.length > 0) {
  console.warn('⚠️  缺少环境变量文件:');
  missingEnvFiles.forEach(file => console.log(`   ${file}`));
  console.log('   请创建相应的环境变量文件');
} else {
  console.log('✅ 环境变量文件完整');
}

// 检查 TypeScript 配置
if (!fs.existsSync('tsconfig.json')) {
  console.error('❌ 缺少 tsconfig.json 文件');
  process.exit(1);
} else {
  console.log('✅ TypeScript 配置完整');
}

// 检查 Vite 配置
if (!fs.existsSync('vite.config.ts') && !fs.existsSync('vite.config.js')) {
  console.error('❌ 缺少 Vite 配置文件');
  process.exit(1);
} else {
  console.log('✅ Vite 配置完整');
}

// 检查源代码目录
const srcDir = 'src';
if (!fs.existsSync(srcDir)) {
  console.error(`❌ 缺少源代码目录: ${srcDir}`);
  process.exit(1);
} else {
  console.log('✅ 源代码目录完整');
}

console.log('\n🎉 环境检查完成！');
console.log('\n运行以下命令启动开发服务器:');
console.log(`   ${packageManager} run dev`);
console.log('\n或构建生产版本:');
console.log(`   ${packageManager} run build`);