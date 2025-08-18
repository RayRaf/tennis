// Утилита для мониторинга производительности
window.PerformanceMonitor = (function() {
    let isMonitoring = false;
    let frameCount = 0;
    let lastTime = performance.now();
    let fps = 0;
    let fpsDisplay = null;
    
    const createFpsDisplay = () => {
        const display = document.createElement('div');
        display.id = 'fps-monitor';
        display.style.cssText = `
            position: fixed;
            top: 10px;
            left: 10px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 12px;
            z-index: 10000;
            pointer-events: none;
            backdrop-filter: blur(5px);
        `;
        document.body.appendChild(display);
        return display;
    };
    
    const updateFps = () => {
        frameCount++;
        const currentTime = performance.now();
        
        if (currentTime >= lastTime + 1000) {
            fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
            frameCount = 0;
            lastTime = currentTime;
            
            if (fpsDisplay) {
                const performance_mode = UI.getPerformanceMode();
                const color = fps >= 55 ? '#4ade80' : fps >= 30 ? '#fbbf24' : '#ef4444';
                fpsDisplay.innerHTML = `
                    <div style="color: ${color}">FPS: ${fps}</div>
                    <div style="color: #94a3b8; font-size: 10px;">Mode: ${performance_mode}</div>
                `;
            }
        }
        
        if (isMonitoring) {
            requestAnimationFrame(updateFps);
        }
    };
    
    const start = () => {
        if (isMonitoring) return;
        
        isMonitoring = true;
        frameCount = 0;
        lastTime = performance.now();
        
        if (!fpsDisplay) {
            fpsDisplay = createFpsDisplay();
        }
        
        requestAnimationFrame(updateFps);
        console.log('🔍 Performance monitoring started');
    };
    
    const stop = () => {
        isMonitoring = false;
        
        if (fpsDisplay) {
            fpsDisplay.remove();
            fpsDisplay = null;
        }
        
        console.log('⏹️ Performance monitoring stopped');
    };
    
    const toggle = () => {
        if (isMonitoring) {
            stop();
        } else {
            start();
        }
    };
    
    const benchmark = () => {
        const results = {
            device: {
                cores: navigator.hardwareConcurrency || 'unknown',
                memory: navigator.deviceMemory ? `${navigator.deviceMemory}GB` : 'unknown',
                connection: navigator.connection ? navigator.connection.effectiveType : 'unknown',
                reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches
            },
            performance: {
                currentMode: UI.getPerformanceMode(),
                currentFPS: fps,
                timestamp: new Date().toISOString()
            }
        };
        
        console.table(results.device);
        console.table(results.performance);
        
        return results;
    };
    
    // Auto-start in development
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        setTimeout(start, 1000);
    }
    
    return {
        start,
        stop,
        toggle,
        benchmark,
        getFPS: () => fps,
        isRunning: () => isMonitoring
    };
})();

// Добавляем горячие клавиши для разработки
document.addEventListener('keydown', (e) => {
    // Ctrl + Shift + P - переключить монитор производительности
    if (e.ctrlKey && e.shiftKey && e.key === 'P') {
        e.preventDefault();
        PerformanceMonitor.toggle();
    }
    
    // Ctrl + Shift + B - бенчмарк
    if (e.ctrlKey && e.shiftKey && e.key === 'B') {
        e.preventDefault();
        PerformanceMonitor.benchmark();
    }
    
    // Ctrl + Shift + 1,2,3 - переключение режимов производительности
    if (e.ctrlKey && e.shiftKey) {
        switch(e.key) {
            case '1':
                e.preventDefault();
                UI.setPerformanceMode('performance');
                console.log('🚀 Switched to Performance mode');
                break;
            case '2':
                e.preventDefault();
                UI.setPerformanceMode('balanced');
                console.log('⚖️ Switched to Balanced mode');
                break;
            case '3':
                e.preventDefault();
                UI.setPerformanceMode('visual');
                console.log('✨ Switched to Visual mode');
                break;
        }
    }
});

console.log(`
🎯 Performance Tools Available:
• Ctrl+Shift+P - Toggle FPS monitor
• Ctrl+Shift+B - Run benchmark
• Ctrl+Shift+1 - Performance mode
• Ctrl+Shift+2 - Balanced mode  
• Ctrl+Shift+3 - Visual mode

Or use: PerformanceMonitor.start() / .stop() / .benchmark()
`);
