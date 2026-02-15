import { Link } from 'react-router-dom';
import './Footer.css';

export const Footer = () => {
    return (
        <footer className="footer">
            <div className="container">
                <div className="footer-content">
                    <div className="footer-section">
                        <h3 className="footer-title">고객센터</h3>
                        <ul className="footer-links">
                            <li><Link to="/help">자주 묻는 질문</Link></li>
                            <li><Link to="/contact">1:1 문의</Link></li>
                            <li><Link to="/notice">공지사항</Link></li>
                        </ul>
                    </div>

                    <div className="footer-section">
                        <h3 className="footer-title">회사 정보</h3>
                        <ul className="footer-links">
                            <li><Link to="/about">회사 소개</Link></li>
                            <li><Link to="/terms">이용약관</Link></li>
                            <li><Link to="/privacy">개인정보처리방침</Link></li>
                        </ul>
                    </div>

                    <div className="footer-section">
                        <h3 className="footer-title">쇼핑 정보</h3>
                        <ul className="footer-links">
                            <li><Link to="/shipping">배송 안내</Link></li>
                            <li><Link to="/returns">반품/교환</Link></li>
                            <li><Link to="/payment">결제 수단</Link></li>
                        </ul>
                    </div>

                    <div className="footer-section">
                        <h3 className="footer-title">소셜 미디어</h3>
                        <div className="footer-social">
                            <a href="#" className="footer-social-link">Facebook</a>
                            <a href="#" className="footer-social-link">Instagram</a>
                            <a href="#" className="footer-social-link">Twitter</a>
                        </div>
                    </div>
                </div>

                <div className="footer-bottom">
                    <p className="footer-copyright">
                        © 2024 Shopping Mall. All rights reserved.
                    </p>
                    <p className="footer-info">
                        사업자등록번호: 123-45-67890 | 통신판매업신고: 2024-서울강남-12345
                    </p>
                </div>
            </div>
        </footer>
    );
};
