/**
 * Input Component
 * 再利用可能な入力フィールドコンポーネント
 */

import { forwardRef, ReactNode } from 'react';
import { cn } from '@/utils/cn';

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  variant?: 'default' | 'filled';
  inputSize?: 'sm' | 'md' | 'lg';
  icon?: ReactNode;
  iconPosition?: 'left' | 'right';
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      type = 'text',
      label,
      error,
      helperText,
      variant = 'default',
      inputSize = 'md',
      icon,
      iconPosition = 'left',
      id,
      ...props
    },
    ref
  ) => {
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;

    const sizeClasses = {
      sm: icon
        ? iconPosition === 'left'
          ? 'pl-10 pr-3 py-2'
          : 'pl-3 pr-10 py-2'
        : 'px-3 py-2 text-sm',
      md: icon
        ? iconPosition === 'left'
          ? 'pl-12 pr-4 py-3'
          : 'pl-4 pr-12 py-3'
        : 'px-4 py-3 text-base',
      lg: icon
        ? iconPosition === 'left'
          ? 'pl-14 pr-5 py-4'
          : 'pl-5 pr-14 py-4'
        : 'px-5 py-4 text-lg',
    };

    const variantClasses = {
      default:
        'border border-gray-300 bg-white focus:border-primary-500 focus:ring-primary-500',
      filled:
        'border-0 bg-gray-100 focus:bg-white focus:ring-2 focus:ring-primary-500',
    };

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="mb-2 block text-sm font-medium text-gray-700"
          >
            {label}
            {props.required && <span className="ml-1 text-red-500">*</span>}
          </label>
        )}

        <div className="relative">
          {icon && (
            <div
              className={cn(
                'pointer-events-none absolute inset-y-0 flex items-center',
                iconPosition === 'left' ? 'left-0 pl-3' : 'right-0 pr-3'
              )}
            >
              {icon}
            </div>
          )}

          <input
            id={inputId}
            type={type}
            className={cn(
              'w-full rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2',
              sizeClasses[inputSize],
              variantClasses[variant],
              error && 'border-red-300 focus:border-red-500 focus:ring-red-500',
              props.disabled && 'cursor-not-allowed bg-gray-50 text-gray-500',
              className
            )}
            ref={ref}
            {...props}
          />
        </div>

        {error && (
          <p className="mt-2 flex items-center text-sm text-red-600">
            <svg
              className="mr-1 h-4 w-4"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
            {error}
          </p>
        )}

        {helperText && !error && (
          <p className="mt-2 text-sm text-gray-500">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input };
