import { Badge } from '../common/Badge';
import './StockDepletionBadge.css';

export const StockDepletionBadge = ({ depletionEtaMinutes }) => {
    if (!depletionEtaMinutes || depletionEtaMinutes > 60) {
        return null;
    }

    const getVariant = () => {
        if (depletionEtaMinutes <= 10) return 'error';
        if (depletionEtaMinutes <= 30) return 'warning';
        return 'info';
    };

    const getBlink = () => {
        return depletionEtaMinutes <= 10;
    };

    return (
        <Badge
            variant={getVariant()}
            size="small"
            className={`stock-depletion-badge ${getBlink() ? 'blink' : ''}`}
        >
            ⏰ {depletionEtaMinutes}분 내 품절 예상
        </Badge>
    );
};
