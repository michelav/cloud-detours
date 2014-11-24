package br.unifor.ppgia.cloud.core.comm.defaultimpl;

import java.nio.charset.Charset;

import org.zeromq.ZMQ;

import br.unifor.ppgia.cloud.core.comm.Channel;
import br.unifor.ppgia.cloud.core.comm.Event;

public class DefaultChannel implements Channel {

	private ZMQ.Context zContext = null;
	private ZMQ.Socket socket;
	private String endpoint = null;
	private Charset cs = Charset.forName("UTF-8");
	
	private final byte[] END_DELIMITER = "[END]".getBytes(cs);

	public DefaultChannel(String protocol, String address, int port) {
		StringBuilder sb = new StringBuilder(protocol);
		sb.append(address).append("://").append(address).append(":")
				.append(port);
		endpoint = sb.toString();
	}

	public DefaultChannel(String protocol, String address) {
		StringBuilder sb = new StringBuilder(protocol);
		sb.append(address).append("://").append(address);
		endpoint = sb.toString();
	}

	public DefaultChannel(String endpoint) {
		this.endpoint = endpoint;
	}
	
	void setUpContext(ZMQ.Context context) {
		zContext = context;
		
	}

	public void connect() {
		socket = zContext.socket(ZMQ.REQ);
		socket.connect(endpoint);
	}
	
	public void bind() {
		socket = zContext.socket(ZMQ.REP);
		socket.bind(endpoint);
	}

	@Override
	public void sendEvent(Event evt) {
		byte[] evtAsBytes = evt.wire().getBytes(cs);
		socket.send(evtAsBytes, ZMQ.SNDMORE);
//		socket.sendMore();
		byte[] payload = evt.getPayload();
		if (payload != null) {
			socket.send(payload, ZMQ.SNDMORE);
		} 
			socket.send(END_DELIMITER, 0);
	}

	@Override
	public Event recvEvent() {
		String header = socket.recvStr(cs).trim();
		Event evt = new DefaultIOEvent();
		evt.loadMetaData(header);
		
		String payloaded = evt.getInfo("payload");
		
		if("True".equalsIgnoreCase(payloaded)) {
			evt.setPayload(socket.recv());
		}
		socket.recv(); // Removing END delimiter from the channel.
		return evt;
	}

	@Override
	public void close() {
		// Event closeEvt = ChannelProvider.getInstance().getEvent(
		// EventType.CLOSE_EVT);
		// sendEvent(closeEvt);
		// XXX Log Close Event
		socket.setLinger(0);
		socket.close();
	}
}
