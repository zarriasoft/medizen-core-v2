import { useEffect, useRef, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';

const SOCKET_URL = import.meta.env.VITE_WS_URL || 'http://localhost:8000';

let socketInstance: Socket | null = null;

export function getSocket(): Socket | null {
    return socketInstance;
}

export function useSocket(patientId: number | null) {
    const socketRef = useRef<Socket | null>(null);

    useEffect(() => {
        if (!patientId) return;

        const socket = io(SOCKET_URL, {
            transports: ['websocket', 'polling'],
            path: '/socket.io',
        });
        socketRef.current = socket;
        socketInstance = socket;

        socket.on('connect', () => {
            socket.emit('join_patient_room', { patient_id: patientId });
        });

        socket.on('disconnect', () => {
            // auto-reconnect handled by socket.io
        });

        socket.on('appointment_reminder', (data: any) => {
            // Dispatch custom event so any component can listen
            window.dispatchEvent(new CustomEvent('medizen:notification', {
                detail: { ...data, type: 'appointment_reminder' }
            }));
        });

        socket.on('appointment_update', (data: any) => {
            window.dispatchEvent(new CustomEvent('medizen:notification', {
                detail: { ...data, type: 'appointment_update' }
            }));
        });

        return () => {
            socket.disconnect();
            socketRef.current = null;
            socketInstance = null;
        };
    }, [patientId]);

    const emitAppointmentBooked = useCallback((data: any) => {
        socketRef.current?.emit('appointment_booked', data);
    }, []);

    return { emitAppointmentBooked };
}
