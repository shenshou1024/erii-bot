# 主框架补丁说明（晚安模式）

> 对应版本：v0.2.5
> 适用框架：QQagent（TypeScript，`src/` 目录）
> 本目录只归档新增模块与改动说明；`proactive.ts`、`index.ts` 为框架原有文件，改动以补丁形式记录，便于跟随上游升级时重新打补丁。

## 功能

晚安静默模式：

- 收到含「晚安 / 睡啦 / 睡了 / 去睡 / 休息了 / 先睡」等关键词的消息 → 该会话进入静默，**暂停主动发言**
- 收到其他正常消息 → 自动解除静默（开始聊天即恢复）
- 兜底：进入静默后，到**下一个 20:00（晚上八点）**自动解除，不管之后有没有再聊天
- 保留原有定时免打扰时段 `quietHours`（`23:00-08:00`），两者叠加生效
- 晚安模式**只抑制主动发言，不拦截被动回复**：说晚安时机器人仍正常回一句，之后聊天也照常应答

## 新增文件

### `src/persona/goodnight.ts`
晚安静默状态管理（按会话 scope 隔离），导出 `GoodnightMode` 类：

- `observe(scope, text)`：按消息文本进入 / 解除静默
- `isMuted(scope, now?)`：当前是否静默（过兜底恢复点自动清除）
- `leave(scope)`：主动解除
- `static isGoodnightText(text)`：关键词识别

完整源码见本目录 `goodnight.ts`。

## 改动文件一：`src/persona/proactive.ts`

1. 顶部引入类型：
   ```ts
   import type { GoodnightMode } from './goodnight.js';
   ```

2. `ProactiveSpeaker` 构造函数追加可选参数：
   ```ts
   constructor(
     // ...原有 cfg / store / log / context...
     private readonly goodnight?: GoodnightMode,
   ) {}
   ```

3. `decide()` 在免打扰时段闸门之后追加晚安静默闸门：
   ```ts
   // 晚安静默：收到「晚安」后暂停主动发言，开始聊天或到次日 20:00 自动解除
   if (this.goodnight?.isMuted(ctx.scope)) {
     return { speak: false, reason: '晚安静默中' };
   }
   ```

## 改动文件二：`src/index.ts`

1. 顶部引入：
   ```ts
   import { GoodnightMode } from './persona/goodnight.js';
   ```

2. 实例化并注入主动发言器（在 `trigger` 之后）：
   ```ts
   const goodnight = new GoodnightMode();
   const proactive = new ProactiveSpeaker(app.proactive, store, getLogger('proactive'), {
     resolvePersona: (scope, userId) => personaMgr.resolve(scope, userId).persona,
     sharing: () => app.memory.retrieval.crossScopeSharing,
   }, goodnight);
   ```

3. 消息准入通过后观察晚安状态（`gate.allowed` 检查之后）：
   ```ts
   // ---- 晚安静默状态：命中休息关键词进入静默，其余正常消息解除 ----
   goodnight.observe(msg.scope, msg.text);
   ```

## 验证

- `npm run typecheck`（tsc --noEmit）通过，无类型错误
- 晚安模块单元测试 10 例全部通过：初始不静默、关键词识别、普通消息不误判、进入静默、消息解除、次日 20:00 兜底解除、会话间独立
- 主动发言相关性测试 14 例全部通过，无回归
- 重启后 WS 正常连接，机器人上线
