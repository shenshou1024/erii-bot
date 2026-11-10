/**
 * 晚安静默模式
 *
 * - 收到含「晚安」等休息关键词的消息 → 进入静默（按会话 scope），抑制主动发言
 * - 收到其他正常消息 → 退出静默（开始聊天自动恢复）
 * - 兜底：进入静默后，到下一个 20:00（晚上八点）自动解除，不管之后有没有再聊天
 * - 与定时免打扰时段 quietHours 互不影响，两者叠加生效
 *
 * 注意：本模块只抑制「主动发言」，不拦截被动回复——
 * 说晚安时机器人仍回一句晚安，之后正常聊天也照常应答。
 */
export class GoodnightMode {
  /** scope -> 进入晚安的时间戳（ms） */
  private muted = new Map<string, number>();

  /** 识别休息类关键词 */
  static isGoodnightText(text: string): boolean {
    const t = (text || '').trim();
    if (!t) return false;
    return /晚安|睡啦|睡了|去睡|睡觉啦|休息了|先睡/.test(t);
  }

  /**
   * 根据一条用户文本更新静默状态：
   * 命中休息关键词 → 进入静默；其余正常消息 → 解除静默。
   */
  observe(scope: string, text: string): void {
    if (GoodnightMode.isGoodnightText(text)) {
      this.muted.set(scope, Date.now());
    } else {
      this.muted.delete(scope);
    }
  }

  /**
   * 计算兜底恢复时刻：进入晚安后的下一个 20:00。
   * 若进入时当天 20:00 已过，则顺延到次日 20:00。
   */
  private restoreAt(enterAt: number): number {
    const restore = new Date(enterAt);
    restore.setHours(20, 0, 0, 0);
    if (restore.getTime() <= enterAt) {
      restore.setDate(restore.getDate() + 1);
    }
    return restore.getTime();
  }

  /** 当前是否处于晚安静默（已过兜底恢复点则自动解除） */
  isMuted(scope: string, now: number = Date.now()): boolean {
    const enterAt = this.muted.get(scope);
    if (enterAt === undefined) return false;
    if (now >= this.restoreAt(enterAt)) {
      this.muted.delete(scope);
      return false;
    }
    return true;
  }

  /** 主动解除静默 */
  leave(scope: string): void {
    this.muted.delete(scope);
  }
}
