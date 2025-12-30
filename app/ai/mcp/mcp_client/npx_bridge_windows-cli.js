
// 自动生成的NPX桥接脚本 for windows-cli
// Package: @simonb97/server-win-cli
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// 所有日志输出到stderr，避免干扰stdout的JSON RPC消息
console.error('[NPX Bridge] Starting @simonb97/server-win-cli...');

// 首先确保包已安装
try {
    // 检查是否已安装
    require.resolve('@simonb97/server-win-cli');
    console.error('[NPX Bridge] Package @simonb97/server-win-cli is already installed');
} catch (e) {
    // 如果未安装，使用npx安装
    console.error('[NPX Bridge] Installing @simonb97/server-win-cli...');
    execSync('npx -y @simonb97/server-win-cli', { stdio: 'inherit' });
}

// 导入并运行包
try {
    require('@simonb97/server-win-cli');
} catch (e) {
    console.error('[NPX Bridge] Failed to run @simonb97/server-win-cli:', e);
    process.exit(1);
}
