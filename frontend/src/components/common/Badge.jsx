import './Badge.css';

export const Badge = ({
    children,
    variant = 'default',
    size = 'medium',
    ...props
}) => {
    const className = [
        'badge',
        `badge-${variant}`,
        `badge-${size}`
    ].filter(Boolean).join(' ');

    return (
        <span className={className} {...props}>
            {children}
        </span>
    );
};
