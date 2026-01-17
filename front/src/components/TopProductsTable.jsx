import './TopProductsTable.css';

export default function TopProductsTable({ products = [], hideHeader = false }) {
    return (
        <div className="top-products-table">
            {!hideHeader && (
                <div className="table-header">
                    <h3>실시간 TOP 10</h3>
                    <span className="table-subtitle">판매량 기준</span>
                </div>
            )}

            <table>
                <thead>
                    <tr>
                        <th className="col-rank">순위</th>
                        <th className="col-product">상품명</th>
                        <th className="col-sales">판매량</th>
                    </tr>
                </thead>
                <tbody>
                    {products.slice(0, 10).map((product, index) => (
                        <tr key={product.product_id}>
                            <td className="col-rank">
                                {index < 3 ? (
                                    <span className={`rank-badge rank-${index + 1}`}>
                                        {index === 0 && '🥇'}
                                        {index === 1 && '🥈'}
                                        {index === 2 && '🥉'}
                                    </span>
                                ) : (
                                    <span className="rank-number">{index + 1}</span>
                                )}
                            </td>
                            <td className="col-product">
                                <span className="product-name" title={product.product_name}>
                                    {product.product_name}
                                </span>
                            </td>
                            <td className="col-sales">
                                <span className="sales-count">{product.purchase_count}</span>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {products.length === 0 && (
                <div className="empty-state">
                    <p>아직 판매 데이터가 없습니다</p>
                </div>
            )}
        </div>
    );
}
