/**
 * 基本的なテスト例
 */

describe('Basic Tests', () => {
  it('should pass basic test', () => {
    expect(1 + 1).toBe(2);
  });

  it('should handle string operations', () => {
    const greeting = 'Hello, World!';
    expect(greeting).toContain('World');
  });

  it('should work with arrays', () => {
    const items = ['Next.js', 'Tailwind CSS', 'TypeScript'];
    expect(items).toHaveLength(3);
    expect(items).toContain('Next.js');
  });
});
