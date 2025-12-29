import './Card.css';

export const Card = ({
    children,
    hover = false,
    padding = 'medium',
    className = '',
    onClick,
    ...props
}) => {
    const cardClassName = [
        'card',
        `card-padding-${padding}`,
        hover ? 'card-hover' : '',
        className
    ].filter(Boolean).join(' ');

    return (
        <div className={cardClassName} onClick={onClick} {...props}>
            {children}
        </div>
    );
};
