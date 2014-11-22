package br.unifor.ppgia.cloud.core.comm;

public interface Channel {
	
	public void connect();
	public void bind();
	public void sendEvent(Event evt);
	public Event recvEvent();
	public void close();

}
