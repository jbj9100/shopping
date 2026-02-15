import { useEffect, useRef, useCallback, useState } from 'react';

export const useWebSocket = (url, options = {}) => {
    const {
        onOpen,
        onMessage,
        onError,
        onClose,
        reconnectInterval = 3000,
        maxReconnectAttempts = 5
    } = options;

    const wsRef = useRef(null);
    const reconnectAttemptsRef = useRef(0);
    const reconnectTimeoutRef = useRef(null);
    const [isConnected, setIsConnected] = useState(false);
    const [lastMessage, setLastMessage] = useState(null);
    const isUnmountedRef = useRef(false);  // 언마운트 추적

    const connect = useCallback(() => {
        // 언마운트된 경우 연결하지 않음
        if (isUnmountedRef.current) return;

        if (wsRef.current?.readyState === WebSocket.OPEN) {
            return;
        }

        try {
            const ws = new WebSocket(url);

            ws.onopen = (event) => {
                console.log('WebSocket connected');
                setIsConnected(true);
                reconnectAttemptsRef.current = 0;
                onOpen?.(event);
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    setLastMessage(data);
                    onMessage?.(data);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };

            ws.onerror = (event) => {
                console.error('WebSocket error:', event);
                onError?.(event);
            };

            ws.onclose = (event) => {
                console.log('WebSocket disconnected');
                setIsConnected(false);
                wsRef.current = null;  // 참조 정리
                onClose?.(event);

                // 언마운트되지 않은 경우에만 재연결 시도
                if (!isUnmountedRef.current && reconnectAttemptsRef.current < maxReconnectAttempts) {
                    reconnectAttemptsRef.current += 1;
                    console.log(`Reconnecting... Attempt ${reconnectAttemptsRef.current}`);
                    reconnectTimeoutRef.current = setTimeout(connect, reconnectInterval);
                }
            };

            wsRef.current = ws;
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
        }
    }, [url, onOpen, onMessage, onError, onClose, reconnectInterval, maxReconnectAttempts]);

    const disconnect = useCallback(() => {
        // 재연결 타이머 정리
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = null;
        }

        // WebSocket 연결 종료
        if (wsRef.current) {
            // 이미 닫힌 상태가 아니면 명시적으로 종료
            if (wsRef.current.readyState !== WebSocket.CLOSED &&
                wsRef.current.readyState !== WebSocket.CLOSING) {
                wsRef.current.close();
            }
            wsRef.current = null;
        }

        setIsConnected(false);
        console.log('WebSocket manually disconnected');
    }, []);

    const sendMessage = useCallback((data) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(data));
        } else {
            console.warn('WebSocket is not connected');
        }
    }, []);

    useEffect(() => {
        isUnmountedRef.current = false;
        connect();

        return () => {
            // cleanup: 언마운트 시
            console.log('WebSocket hook unmounting - cleaning up');
            isUnmountedRef.current = true;  // 언마운트 플래그 설정
            disconnect();
        };
    }, [url]); // ✅ url이 변경될 때만 재연결

    return {
        isConnected,
        lastMessage,
        sendMessage,
        disconnect,
        reconnect: connect
    };
};

