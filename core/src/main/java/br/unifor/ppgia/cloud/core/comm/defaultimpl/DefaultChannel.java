package br.unifor.ppgia.cloud.core.comm.defaultimpl;

import org.zeromq.ZMQ;

import br.unifor.ppgia.cloud.core.comm.Channel;
import br.unifor.ppgia.cloud.core.comm.Event;

public class DefaultChannel implements Channel {

	private static ZMQ.Context zContext = ZMQ.context(1);
	private ZMQ.Socket socket;
	
	private final String END_DELIMITER = "[END]";

	public DefaultChannel(String protocol, String address, int port) {
		StringBuilder sb = new StringBuilder(protocol);
		sb.append(address).append("://").append(address).append(":")
				.append(port);
		createConnection(sb.toString());
	}

	public DefaultChannel(String protocol, String address) {
		StringBuilder sb = new StringBuilder(protocol);
		sb.append(address).append("://").append(address);
		createConnection(sb.toString());
	}

	public DefaultChannel(String endpoint) {
		createConnection(endpoint);
	}

	private void createConnection(String endpoint) {
		socket = zContext.socket(ZMQ.REQ);
		socket.connect(endpoint);
	}

	@Override
	public void sendEvent(Event evt) {
		socket.sendMore(evt.wire());
		byte[] payload = evt.getPayload();
		if (payload != null) {
			socket.send(payload, 0);
		} else {
			socket.send(END_DELIMITER, 0);
		}
	}

	@Override
	public Event recvEvent() {
		String header = (new String(socket.recv())).trim();
		Event evt = new DefaultIOEvent();
		evt.loadMetaData(header);
		if (socket.hasReceiveMore()) {
			evt.setPayload(socket.recv());
		}
		return evt;
	}

	@Override
	public void close() {
		// Event closeEvt = ChannelProvider.getInstance().getEvent(
		// EventType.CLOSE_EVT);
		// sendEvent(closeEvt);

		// XXX Log Close Event
		socket.close();
	}
}
